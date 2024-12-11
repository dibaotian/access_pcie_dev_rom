import os
import mmap
import struct
import time

def read_pcie_rom(output_file, rom_base_addr, rom_size=512 * 1024):
    """
    Read PCIe device Option ROM space and save to a file.

    :param output_file: Path to save the ROM content.
    :param rom_base_addr: Physical base address of the PCIe Option ROM.
    :param rom_size: Size of the ROM to read (default 512KB).
    """
    # Ensure running as root
    if os.geteuid() != 0:
        raise PermissionError("This script requires root privileges.")

    # Open /dev/mem for raw physical memory access
    try:

        start_time = time.time()  # Start timing

        with open("/dev/mem", "rb") as f:
            # Memory map the ROM region
            mem = mmap.mmap(f.fileno(), length=rom_size, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ, offset=rom_base_addr)

            # Read the data
            rom_data = mem.read(rom_size)
            mem.close()

        # Save the ROM data to a file
        #with open(output_file, "wb") as out_file:
        #    out_file.write(rom_data)

        # Save the ROM data to a file in hexadecimal format
        # with open(output_file, "w") as out_file:
        #    for i in range(0, len(rom_data), 16):
        #        hex_values = ' '.join(f"{byte:02X}" for byte in rom_data[i:i+16])
        #        out_file.write(hex_values + "\n")

        # Save the ROM data to a file in specified hexadecimal format
        with open(output_file, "w") as out_file:
            for i in range(0, len(rom_data), 4):
                # Read 32-bit chunks and reverse for little-endian representation
                chunk = rom_data[i:i+4]
                if len(chunk) == 4:
                    value = struct.unpack("<I", chunk)[0]
                    out_file.write(f"{value:08X},\n")

        end_time = time.time()  # End
        elapsed_time = end_time - start_time

        print(f"Time taken to read ROM: {elapsed_time:.6f} seconds")
        print(f"ROM content saved to {output_file}")

    except FileNotFoundError:
        print("/dev/mem is not available on this system.")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    ROM_BASE_ADDR = 0xec300000
    OUTPUT_FILE = "pcie_rom.bin"

    try:
        read_pcie_rom(OUTPUT_FILE, ROM_BASE_ADDR)
    except Exception as e:
        print(f"Failed to read PCIe ROM: {e}")

