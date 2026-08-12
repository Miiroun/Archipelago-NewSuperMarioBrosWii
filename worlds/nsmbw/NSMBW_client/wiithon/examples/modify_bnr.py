from io import BytesIO
from wiithon.disc.patcher import WiiIsoPatcher
from wiithon.formats.bnr import BNR

ISO_PATH = "../assets/smg.iso"
OUT_PATH = "../assets/game_patched.iso"

def main():
    with WiiIsoPatcher(ISO_PATH) as patcher:
        bnr_bytes = patcher.read_file("opening.bnr")
        bnr = BNR.read(BytesIO(bnr_bytes))

        print(repr(bnr))
        # BNR title='Super Mario Galaxy'
        # IMET  icon=0x...  banner=0x...  sound=0x...
        #   Japanese  : スーパーマリオギャラクシー
        #   English   : Super Mario Galaxy
        #   ...

        bnr.imet.set_title("Modded game", language="English")

        icon_bytes = bnr.get_icon()  # meta/icon.bin   (IMD5 + LZ77 + U8 + TPL)
        banner_bytes = bnr.get_banner()  # meta/banner.bin (same)
        sound_bytes = bnr.get_sound()  # meta/sound.bin  (IMD5 + BNS/WAV/AIFF)

        print(f"icon   : {len(icon_bytes):#x} bytes")
        print(f"banner : {len(banner_bytes):#x} bytes")
        print(f"sound  : {len(sound_bytes):#x} bytes")

        with open("../extract/icon.bin", "wb") as f: f.write(icon_bytes)
        with open("../extract/banner.bin", "wb") as f: f.write(banner_bytes)
        with open("../extract/sound.bin", "wb") as f: f.write(sound_bytes)

        # with open("my_custom_sound.bin", "rb") as f:
        #     custom_sound = f.read()
        #
        # bnr.replace_sound(custom_sound)

        patcher.replace_file("opening.bnr", bnr.get_bytes())

        patcher.build(OUT_PATH)
        print(f"ISO written : {OUT_PATH}")


if __name__ == "__main__":
    main()
