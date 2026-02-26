from typing import Optional, List

from MultiServer import mark_raw
from NSMBWInterface import *
from NetUtils import NetworkItem
from NotificationManager import NotificationManager


tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop

    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop


logger = logging.getLogger("Client")


class NSMBWCommandProcessor(ClientCommandProcessor):
    ctx: "NSMBWContext"

    def __init__(self, ctx: "NSMBWContext"):
        super().__init__(ctx)

    def _cmd_test_hud(self, *args: List[Any]):
        """Send a message to the game interface."""
        self.ctx.notification_manager.queue_notification(" ".join(map(str, args)))

    def _cmd_status(self, *args: List[Any]):
        """Display the current dolphin connection status."""
        logger.info(f"Connection status: {status_messages[self.ctx.connection_state]}")

    def _cmd_deathlink(self):
        """Toggle deathlink from client. Overrides default setting."""
        self.ctx.death_link_enabled = not self.ctx.death_link_enabled
        Utils.async_start(
            self.ctx.update_death_link(self.ctx.death_link_enabled),
            name="Update Deathlink",
        )
        message = (
            f"Deathlink {'enabled' if self.ctx.death_link_enabled else 'disabled'}"
        )
        logger.info(message)
        self.ctx.notification_manager.queue_notification(message)

    def _cmc_reapply_checks(self):
        """Do this command if some checks havent been aplied"""
        self.ctx.items_handled = []
        self.ctx.locations_handled = []

    @mark_raw
    def _cmd_locationscout(self, key: str =""):
        """"scout location"""
        self.ctx.send_msgs([{"cmd": "LocationScouts", "locations": key}])

    @mark_raw
    def _cmd_sendlocation(self, key: str =""):
        """Send item check"""
        self.ctx.send_msgs([{"cmd": "LocationChecks", "locations": key}])
        self.connection_status = ConnectionState.SCOUTS_SENT


status_messages = {
    ConnectionState.IN_GAME: "Connected to New super mario bros wii",
    ConnectionState.IN_MENU: "Connected to game, waiting for game to start",
    ConnectionState.DISCONNECTED: "Unable to connect to the Dolphin instance, attempting to reconnect...",
    ConnectionState.MULTIPLE_DOLPHIN_INSTANCES: "Warning: Multiple Dolphin instances detected, client may not function correctly.",
    ConnectionState.SCOUTS_SENT: "Sent location scout",
}

class NSMBWContext(SuperContext):
        # Text Mode to use !hint and such with games that have no text entry
        tags = {"AP"}#CommonContext.tags
        game = 'NSMBW'  # empty matches any game since 0.3.2
        items_handling = 0b111  # receive all items for /received
        want_slot_data = True  # Can't use game specific slot_data
        game_interface: NSMBWInterface
        connection_state = ConnectionState.DISCONNECTED
        last_error_message: Optional[str] = None
        dolphin_sync_task: Optional[asyncio.Task[Any]] = None
        notification_manager: NotificationManager
        death_link_enabled = False
        command_processor = NSMBWCommandProcessor
        apnsmbw_file: Optional[str] = None
        slot_data: Dict[str, Utils.Any] = {}


        #Created for NSMBW
        items_handled = []
        locations_handled = []

        def __init__(self, server_address: str, password: str, apnsmbw_file: Optional[str] = None):
            super().__init__(server_address, password)
            self.game_interface = NSMBWInterface(logger)
            self.notification_manager = NotificationManager(HUD_MESSAGE_DURATION, self.game_interface.send_hud_message)
            self.apnsmbw_file = apnsmbw_file
            self.items_handled = []

        async def server_auth(self, password_requested: bool = False):
            if password_requested and not self.password:
                await super(NSMBWContext, self).server_auth(password_requested)
            await self.get_username()
            await self.send_connect()

        def on_package(self, cmd: str, args: dict):
            super().on_package(cmd, args)
            if cmd == "Connected":
                if tracker_loaded:
                    args.setdefault("slot_data", dict())
            elif cmd == "ReceivedItems":
                #handle_recived_items
                pass
            elif cmd == "Bounced":
                print("Packed bounced with the following argument")
                print(args)
            elif cmd == "PrintJSON":
                print("Packed PrintJSON with the following argument")
                print(args)
            elif cmd == "Retrieved":
                print("Packed Retrieved with the following argument")
                print(args)
            else:
                print(f"Recived package with command: {cmd}")

        async def disconnect(self, allow_autoreconnect: bool = False):
            await super().disconnect(allow_autoreconnect)

