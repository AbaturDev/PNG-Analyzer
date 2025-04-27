from struct import unpack, pack

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'  # PNG signature


def is_critical_chunk(chunk_type: str, color_type: int | None) -> bool:
    if chunk_type == 'PLTE':
        if color_type == 0 or 4:
            raise ValueError(f"PNG file of color type {color_type} cannot have PLTE chunk!")

        if color_type == 3:
            return True
        else:
            return False

    return chunk_type.isupper()


def anonymize_png(input_filepath: str, output_filepath: str) -> None:
    color_type = None

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

            if is_critical_chunk(chunk_type_str, color_type):
                if chunk_type_str == 'IHDR':
                    color_type = data[9]
                    print(f"Detected color_type: {color_type}")

                f_out.write(pack(">I", length))
                f_out.write(chunk_type)
                f_out.write(data)
                f_out.write(pack(">I", crc))
                print(f"{chunk_type_str} is a critical chunk. Writing to output file.")
            else:
                print(f"Removing {chunk_type_str} chunk (ancillary chunk).")

            if chunk_type_str == 'IEND':
                break

    print("Anonymization complete!")
