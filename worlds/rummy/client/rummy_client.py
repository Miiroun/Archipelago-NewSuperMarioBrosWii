import asyncio
import sys
from argparse import Namespace
from enum import Enum
from typing import TYPE_CHECKING, Any

from NetUtils import ClientStatus
from Utils import gui_enabled
from worlds.rummy.Common import RUMMY_NAME
from worlds.sc2.mission_order import slot_data

from ..game.events import LocationClearedEvent, VictoryEvent
from ..game.game import Game
from ..game.inputs import Input
from .game_manager import RummyManager
from .graphics import PlayerSprite
from .item_quality import get_quality_for_network_item
from .sounds import (
    ITEM_JINGLES,
    VICTORY_JINGLE,
)

tracker_loaded = False

try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperCommonContext, get_base_parser, handle_url_arg, logging, \
    TrackerCommandProcessor as SuperClientCommandProcessor, CommonContext, asyncio, server_loop, updateTracker

    tracker_loaded = True
    print("Tracker is loaded")
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperCommonContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor as SuperClientCommandProcessor, CommonContext, asyncio, server_loop
    print("Tracker was not found so is not loaded")
logger = logging.getLogger("Client")


if TYPE_CHECKING:
    import kvui


# !!! IMPORTANT !!!
# The client implementation is *not* meant for teaching.
# Obviously, it is written to the best of its author's abilities,
# but it is not to the same standard as the rest of the apworld.
# Copy things from here at your own risk.


class ConnectionStatus(Enum):
    NOT_CONNECTED = 0
    SCOUTS_NOT_SENT = 1
    SCOUTS_SENT = 2
    GAME_RUNNING = 3


class RummyClientCommandProcessor(SuperClientCommandProcessor):
    ctx: "RummyContext"



class RummyContext(SuperCommonContext):
    game = RUMMY_NAME
    items_handling = 0b111  # full remote

    client_loop: asyncio.Task[None]

    last_connected_slot: int | None = None

    slot_data: dict[str, Any]

    rummy_game: Game | None = None
    hard_mode: bool = False
    hammer: bool = False
    extra_starting_chest: bool = False
    player_sprite: PlayerSprite = PlayerSprite.HUMAN

    connection_status: ConnectionStatus = ConnectionStatus.NOT_CONNECTED

    highest_processed_item_index: int = 0
    queued_locations: list[int]

    delay_intro_song: bool

    ui: RummyManager
    command_processor = RummyClientCommandProcessor

    def __init__(
        self, server_address: str | None = None, password: str | None = None, delay_intro_song: bool = False
    ) -> None:
        super().__init__(server_address, password)

        self.queued_locations = []
        self.slot_data = {}
        self.delay_intro_song = delay_intro_song

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            self.ui.allow_intro_song()
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    def handle_connection_loss(self, msg: str) -> None:
        self.ui.allow_intro_song()
        super().handle_connection_loss(msg)

    async def connect(self, address: str | None = None) -> None:
        self.ui.switch_to_regular_tab()
        await super().connect(address)

    async def rummy_loop(self) -> None:
        while not self.exit_event.is_set():
            if self.connection_status != ConnectionStatus.GAME_RUNNING:
                if self.connection_status == ConnectionStatus.SCOUTS_NOT_SENT:
                    await self.send_msgs([{"cmd": "LocationScouts", "locations": self.server_locations}])
                    self.connection_status = ConnectionStatus.SCOUTS_SENT

                await asyncio.sleep(0.1)
                continue

            if not self.rummy_game or not self.rummy_game.gameboard or not self.rummy_game.gameboard.ready:
                await asyncio.sleep(0.1)
                continue

            try:
                while self.queued_locations:
                    location = self.queued_locations.pop(0)
                    self.location_checked_side_effects(location)
                    self.locations_checked.add(location)
                    await self.check_locations({location})

                rerender = False

                new_items = self.items_received[self.highest_processed_item_index :]
                for item in new_items:
                    self.highest_processed_item_index += 1
                    self.rummy_game.receive_item(item.item, item.location, item.player)
                    rerender = True

                for new_remotely_cleared_location in self.checked_locations - self.locations_checked:
                    self.rummy_game.force_clear_location(new_remotely_cleared_location)
                    rerender = True

                if rerender:
                    self.render()

                if self.rummy_game.has_won and not self.finished_game:
                    await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIEN_GOAL}])
                    self.finished_game = True
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(0.1)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "ConnectionRefused":
            self.ui.allow_intro_song()

        if cmd == "Connected":
            if self.connection_status == ConnectionStatus.GAME_RUNNING:
                # In a connection loss -> auto reconnect scenario, we can seamlessly keep going
                return

            self.last_connected_slot = self.slot

            self.connection_status = ConnectionStatus.NOT_CONNECTED  # for safety, it will get set again later

            self.slot_data = args["slot_data"]


            self.rummy_game = Game(self.slot_data["card_order"])
            self.highest_processed_item_index = 0
            self.render()

            self.connection_status = ConnectionStatus.SCOUTS_NOT_SENT
        if cmd == "LocationInfo":
            remote_item_graphic_overrides = {
                Location(location): Item(network_item.item)
                for location, network_item in self.locations_info.items()
                if self.slot_info[network_item.player].game == self.game
            }

            assert self.rummy_game is not None
            #self.rummy_game.gameboard.fill_remote_location_content(remote_item_graphic_overrides)
            self.render()

            self.connection_status = ConnectionStatus.GAME_RUNNING
            self.ui.game_started()

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        self.finished_game = False
        self.locations_checked = set()
        self.connection_status = ConnectionStatus.NOT_CONNECTED
        await super().disconnect(*args, **kwargs)

    def render(self) -> None:
        if self.rummy_game is None:
            raise RuntimeError("Tried to render before self.rummy_game was initialized.")

        self.ui.render(self.rummy_game)
        self.handle_game_events()

    def location_checked_side_effects(self, location: int) -> None:
        network_item = self.locations_info[location]


        item_quality = get_quality_for_network_item(network_item)
        self.play_jingle(ITEM_JINGLES[item_quality])

    def play_jingle(self, audio_filename: str) -> None:
        self.ui.play_jingle(audio_filename)

    def handle_game_events(self) -> None:
        if self.rummy_game is None:
            return

        while self.rummy_game.queued_events:
            event = self.rummy_game.queued_events.pop(0)

            if isinstance(event, LocationClearedEvent):
                self.queued_locations.append(event.location_id)
                continue

            if isinstance(event, VictoryEvent):
                self.play_jingle(VICTORY_JINGLE)
                continue

    def input_and_rerender(self, input_key: Input) -> None:
        if self.rummy_game is None:
            return
        if not self.rummy_game.gameboard.ready:
            return
        self.rummy_game.input(input_key)
        self.render()

    def queue_auto_move(self, target_x: int, target_y: int) -> None:
        if self.rummy_game is None:
            return
        if not self.rummy_game.gameboard.ready:
            return
        if not self.ui.game_view.focused > 1:  # Must already be in focus
            return
        self.rummy_game.queue_auto_move(target_x, target_y)
        self.ui.start_auto_move()

    def do_auto_move_and_rerender(self) -> None:
        if self.rummy_game is None:
            return
        if not self.rummy_game.gameboard.ready:
            return
        changed = self.rummy_game.do_auto_move()
        if changed:
            self.render()



    def make_gui(self) -> "type[kvui.GameManager]":
        self.load_kv()
        return RummyManager

    def load_kv(self) -> None:
        import pkgutil

        from kivy.lang import Builder

        data = pkgutil.get_data(__name__, "rummy_client.kv")
        if data is None:
            raise RuntimeError("rummy_client.kv could not be loaded.")

        Builder.load_string(data.decode())


async def main(args: Namespace) -> None:
    if not gui_enabled:
        raise RuntimeError("Rummy cannot be played without gui.")

    # Assume we shouldn't play the intro song in the auto-connect scenario, because the game will instantly start.
    delay_intro_song = args.connect and args.name

    ctx = RummyContext(args.connect, args.password, delay_intro_song=delay_intro_song)
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    ctx.run_gui()
    ctx.run_cli()

    ctx.client_loop = asyncio.create_task(ctx.rummy_loop(), name="Client Loop")

    await ctx.exit_event.wait()
    await ctx.shutdown()


def launch(*args: str) -> None:
    from .launch import launch_rummy_client

    launch_rummy_client(*args)


if __name__ == "__main__":
    launch(*sys.argv[1:])
