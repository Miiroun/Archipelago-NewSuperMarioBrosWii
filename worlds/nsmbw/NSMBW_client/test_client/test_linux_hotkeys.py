"""Check Linux hotkeys without connecting to Dolphin or sending input."""
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class TestLinuxHotkeys(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = SimpleNamespace(keypress_library=1, dolphin_process_name="")
        # Client dependencies are not required for world generation or its test suite.
        self.enterContext(patch.dict("sys.modules", {"dolphin_memory_engine": Mock(), "psutil": Mock()}))
        self.enterContext(patch.dict("os.environ"))
        self.enterContext(patch("Utils.get_settings", return_value={"nsmbw_settings": self.settings}))
        from .. import NSMBWInterface as client

        self.run = self.enterContext(patch.object(client.subprocess, "run"))
        self.enterContext(patch.object(client.shutil, "which", return_value="/usr/bin/tool"))
        self.interface = client.NSMBWInterface(Mock(), Mock(), Mock())

    def test_save_and_load_commands(self) -> None:
        for slot in range(1, 9):
            for backend in (1, 2):
                for shift in (False, True):
                    with self.subTest(slot=slot, backend=backend, shift=shift):
                        self.settings.keypress_library = backend
                        self.assertTrue(self.interface._linux_send_hotkey(slot, shift))
                        if backend == 1:
                            command = ["xdotool", "key", "--clearmodifiers",
                                       ("shift+" if shift else "") + f"F{slot}"]
                        else:
                            keys = [f"{58 + slot}:1", f"{58 + slot}:0"]
                            command = ["ydotool", "key", *(["42:1", *keys, "42:0"] if shift else keys)]
                        self.run.assert_called_with(command, check=True, capture_output=True)

    def test_error_includes_stderr_and_actual_slot(self) -> None:
        self.run.side_effect = subprocess.CalledProcessError(2, "xdotool", stderr=b"Unknown key")
        self.assertFalse(self.interface._linux_send_hotkey(7, True))
        message = self.interface.log_color.call_args.args[0]
        self.assertIn("Unknown key", message)
        self.assertIn("F7", message)
        self.assertNotIn("F8", message)
