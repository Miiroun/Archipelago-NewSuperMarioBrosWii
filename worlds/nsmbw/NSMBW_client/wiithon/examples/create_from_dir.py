import os
from wiithon.builder.directory_source import DirectoryPartitionSource
from wiithon.builder.disc_builder import WiiDiscBuilder
from wiithon.disc.enums import WiiPartType
from wiithon.disc.structs.disc_header import DiscHeader

# May adding all this logic into one file maybe ?
def main():
    src_dir = "../src_dir/DATA"
    
    # Reading header & region
    sys_path = os.path.join(src_dir, "sys", "boot.bin")
    region_path = os.path.join(src_dir, "disc", "region.bin")

    with open(sys_path, "rb") as f:
        disc_header = DiscHeader.read(f)
        disc_header.disable_disc_encryption = 0
        disc_header.disable_hash_verification = 0

    with open(region_path, "rb") as f:
        region = f.read(32)

    # Partition builder with the correct part type
    dir_builder = DirectoryPartitionSource(src_dir, WiiPartType.DATA)
    
    # Writing Iso
    output_iso = "../assets/copied_dir.iso"
    os.makedirs(os.path.dirname(output_iso), exist_ok=True)
    
    with open(output_iso, "w+b") as dest:
        builder = WiiDiscBuilder(disc_header, region)
        builder.add_partition(dest, dir_builder, None)
        builder.finish(dest)
        
        print("Done")

if __name__ == "__main__":
    main()