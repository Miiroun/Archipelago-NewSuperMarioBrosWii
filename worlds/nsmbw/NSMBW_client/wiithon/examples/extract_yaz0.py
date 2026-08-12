from wiithon.formats.yaz0 import Yaz0

def main():
    src_path = "../assets/AstroDomeScenario.szs"
    dest_path = "../assets/AstroDomeScenario.arc"

    with open(src_path, "rb") as f:
        yaz0 = Yaz0.read(f)

    with open(dest_path, "wb") as f:
        f.write(yaz0.data)

if __name__ == "__main__":
    main()