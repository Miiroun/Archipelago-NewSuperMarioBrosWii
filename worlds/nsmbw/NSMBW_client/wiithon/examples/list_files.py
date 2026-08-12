from wiithon.disc.reader import WiiIsoReader

def main():
    # Opening the iso with WiiIsoReader
    with WiiIsoReader("../assets/smg.iso") as reader:
        print(f"Game: {reader.disc_header.game_title}")

        data = reader.get_data_partition()
        partition = reader.open_partition(data)

        # List files
        for path in partition.list_files():
            print(path)


        print(f"Number of files: {len(partition.list_files())}")


if __name__ == "__main__":
    main()