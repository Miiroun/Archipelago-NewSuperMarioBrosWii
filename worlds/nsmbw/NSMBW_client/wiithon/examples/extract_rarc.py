import os
from wiithon.formats.rarc import Rarc

def main():
    input_file = "../assets/AstroDomeScenario.arc"

    base_name = os.path.splitext(input_file)[0]
    output_dir = f"{base_name}_extracted"

    try:
        with open(input_file, "rb") as f:
            rarc_archive = Rarc.read(f)
            
            print(f"Archive contains {rarc_archive.number_nodes} nodes and {rarc_archive.total_directory} entries.")
            print(f"Extracting to: {output_dir}")
            
            rarc_archive.extract_to(output_dir)
            
            print("Extraction successful!")
    except Exception as e:
        print(f"An error occurred during extraction: {e}")

if __name__ == "__main__":
    main()
