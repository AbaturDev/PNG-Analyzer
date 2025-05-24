from struct import unpack, pack
from zlib import crc32

# PNG signature (1st 8 bytes of every valid PNG file)
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

# Critical chunks that must be specifically handled
CRITICAL_CHUNKS = {'IHDR', 'PLTE', 'IDAT', 'IEND'}

# Determines where a chunk should be kept in the output file
def is_critical_chunk(chunk_type: str, color_type: int | None) -> bool:
    if chunk_type in CRITICAL_CHUNKS:
        if chunk_type == 'PLTE':
            # PLTE chunk is not valid for files with color type 0 or 4
            if color_type == 0 or 4:
                raise ValueError(f"Bad PNG file. PNG file of color type {color_type} cannot have PLTE chunk!")
            # File with color type must have the PLTE chunk, otherwise the chunk is ancillary
            return color_type == 3
        return True
    return False

# Anonymizes PNG file - removes ancillary chunks and merges IDAT chunks
def anonymize_png(input_filepath: str, output_filepath: str) -> None:
    color_type = None  # Will be extracted IHDR chunk
    idat_data = b''  # Will collect IDAT chunks data to merge it

    with open(input_filepath, 'rb') as f_in, open(output_filepath, 'wb') as f_out:
        signature = f_in.read(8)
        if signature != PNG_SIGNATURE:
            # File with bad signature won't be handled
            raise ValueError("Not a valid PNG file.")

        f_out.write(signature)  # Start the output file with the signature

        print(f"Starting anonymization of \"{input_filepath}\"...")
        while True:
            length_bytes = f_in.read(4)
            if len(length_bytes) == 0:
                break  # EOF reached

            length = unpack(">I", length_bytes)[0]
            chunk_type = f_in.read(4)
            chunk_type_str = chunk_type.decode('ascii')  # Convert chunk type to ASCII
            data = f_in.read(length)
            crc = unpack(">I", f_in.read(4))[0]

            # Handle IHDR chunk
            if chunk_type_str == 'IHDR':
                color_type = data[9]  # Extract color type from header
                print(f"Detected color_type: {color_type}")
                print("Writing IHDR chunk...")
                f_out.write(pack(">I", length))
                f_out.write(chunk_type)
                f_out.write(data)
                f_out.write(pack(">I", crc))
                print("IHDR has been written.")

            # Handle IDAT chunk
            elif chunk_type_str == 'IDAT':
                # Collect current IDAT data to merge later
                idat_data += data
                print("Collected IDAT chunk data.")

            # Handle IEND chunk
            elif chunk_type_str == 'IEND':
                if idat_data:
                    # Write a single merged IDAT chunk just before IEND
                    print("Writing merged IDAT chunk...")
                    f_out.write(pack(">I", len(idat_data)))
                    f_out.write(b'IDAT')
                    f_out.write(idat_data)
                    f_out.write(pack(">I", crc32(b'IDAT' + idat_data) & 0xffffffff))
                    print("Merged IDAT chunk has been written.")

                print("Writing IEND chunk...")
                f_out.write(pack(">I", 0))
                f_out.write(chunk_type)
                f_out.write(pack(">I", crc))
                print("IEND chunk has been written.")
                break  # IEND must be the last chunk

            elif is_critical_chunk(chunk_type_str, color_type):
                # Preserve other critical chunks (like PLTE if it's necessary)
                print(f"{chunk_type_str} is a critical chunk. Writing...")
                f_out.write(pack(">I", length))
                f_out.write(chunk_type)
                f_out.write(data)
                f_out.write(pack(">I", crc))
                print(f"{chunk_type_str} has been written.")

            else:
                # Ancillary chunks are skipped
                print(f"Removing {chunk_type_str} chunk (ancillary chunk).")

    print("Anonymization complete!")
