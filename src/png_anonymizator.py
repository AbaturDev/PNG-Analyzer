from struct import unpack, pack
from zlib import crc32

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'  # PNG signature
CRITICAL_CHUNKS = {'IHDR', 'PLTE', 'IDAT', 'IEND'}

def is_critical_chunk(chunk_type: str, color_type: int | None) -> bool:
    if chunk_type in CRITICAL_CHUNKS:
        if chunk_type == 'PLTE':
            if color_type == 0 or 4:
                raise ValueError(f"Bad PNG file. PNG file of color type {color_type} cannot have PLTE chunk!")
            return color_type == 3
        return True
    return False


def anonymize_png(input_filepath: str, output_filepath: str) -> None:
    color_type = None
    idat_data = b''

    with open(input_filepath, 'rb') as f_in, open(output_filepath, 'wb') as f_out:
        signature = f_in.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("Not a valid PNG file.")

        f_out.write(signature)

        print(f"Starting anonymization of \"{input_filepath}\"...")
        while True:
            length_bytes = f_in.read(4)
            if len(length_bytes) == 0:
                break

            length = unpack(">I", length_bytes)[0]
            chunk_type = f_in.read(4)
            chunk_type_str = chunk_type.decode('ascii')
            data = f_in.read(length)
            crc = unpack(">I", f_in.read(4))[0]

            if chunk_type_str == 'IHDR':
                color_type = data[9]
                print(f"Detected color_type: {color_type}")
                print("Writing IHDR chunk...")
                f_out.write(pack(">I", length))
                f_out.write(chunk_type)
                f_out.write(data)
                f_out.write(pack(">I", crc))
                print("IHDR has been written.")

            elif chunk_type_str == 'IDAT':
                idat_data += data
                print("Collected IDAT chunk data.")

            elif chunk_type_str == 'IEND':
                if idat_data:
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
                break

            elif is_critical_chunk(chunk_type_str, color_type):
                print(f"{chunk_type_str} is a critical chunk. Writing...")
                f_out.write(pack(">I", length))
                f_out.write(chunk_type)
                f_out.write(data)
                f_out.write(pack(">I", crc))
                print(f"{chunk_type_str} has been written.")

            else:
                print(f"Removing {chunk_type_str} chunk (ancillary chunk).")

    print("Anonymization complete!")
