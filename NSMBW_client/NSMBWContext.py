from typing import Optional, List

from CommonClient import get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop
from NSMBWInterface import *
from NotificationManager import NotificationManager

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



status_messages = {
    ConnectionState.IN_GAME: "Connected to New super mario bros wii",
    ConnectionState.IN_MENU: "Connected to game, waiting for game to start",
    ConnectionState.DISCONNECTED: "Unable to connect to the Dolphin instance, attempting to reconnect...",
    ConnectionState.MULTIPLE_DOLPHIN_INSTANCES: "Warning: Multiple Dolphin instances detected, client may not function correctly.",
}

class NSMBWContext(CommonContext):
        # Text Mode to use !hint and such with games that have no text entry
        tags = CommonContext.tags
        game = 'NSMBW'  # empty matches any game since 0.3.2
        items_handling = 0b111  # receive all items for /received
        want_slot_data = False  # Can't use game specific slot_data
        game_interface: NSMBWInterface
        connection_state = ConnectionState.DISCONNECTED
        last_error_message: Optional[str] = None
        dolphin_sync_task: Optional[asyncio.Task[Any]] = None
        notification_manager: NotificationManager
        death_link_enabled = False
        command_processor = NSMBWCommandProcessor
        apmp1_file: Optional[str] = None


        def __init__(self, server_address: str, password: str, apmp1_file: Optional[str] = None):
            super().__init__(server_address, password)
            self.game_interface = NSMBWInterface(logger)
            self.notification_manager = NotificationManager(HUD_MESSAGE_DURATION, self.game_interface.send_hud_message)
            self.apmp1_file = apmp1_file
        

        async def server_auth(self, password_requested: bool = False):
            if password_requested and not self.password:
                await super(NSMBWContext, self).server_auth(password_requested)
            await self.get_username()
            await self.send_connect(game="")

        def on_package(self, cmd: str, args: dict):
            if cmd == "Connected":
                self.game = self.slot_info[self.slot].game

        async def disconnect(self, allow_autoreconnect: bool = False):
            self.game = ""
            await super().disconnect(allow_autoreconnect)

