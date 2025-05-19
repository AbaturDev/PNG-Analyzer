from chunks import PngChunk
import struct
import zlib
import piexif
import numpy as np
from collections import Counter


PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

def read_chunks(file_path):
    chunks = []

    with open(file_path, "rb") as f:
        signature = f.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("Not a valid PNG file.")

        while True:
            length_bytes = f.read(4)
            if len(length_bytes) == 0:
                break

            length = struct.unpack(">I", length_bytes)[0]
            chunk_type = f.read(4).decode("ascii")
            data = f.read(length)
            crc = struct.unpack(">I", f.read(4))[0]

            chunk = PngChunk(length, chunk_type, data, crc)
            chunks.append(chunk)

            if chunk_type == "IEND":
                break

    return chunks

def extract_metadata(chunks):
    ihdr_data = None
    idat_data = b""

    for chunk in chunks:
        if chunk.type == "IHDR":
            ihdr_data = parse_IHDR(chunk)
            print("IHDR metadata: " + str(ihdr_data))

        elif chunk.type == "tEXt":
            print("tEXt metadata: " + str(parse_tEXt(chunk)))

        elif chunk.type == "iTXt":
            print("iTXt metadata: " + str(parse_iTXt(chunk)))
        
        elif chunk.type == "tIME":
            print("tIME metadata: " + str(parse_tIME(chunk)))

        elif chunk.type == "eXIf":
            print("eXIf metadata: " + str(parse_eXIf(chunk)))
        
        elif chunk.type == "pHYs":
            print("pHYs metadata: " + str(parse_pHYs(chunk)))

        elif chunk.type == "zTXt":
            print("zTXt metadata: " + str(parse_zTXt(chunk)))
        
        elif chunk.type == "IDAT":
            idat_data += chunk.data

        elif chunk.type == "PLTE":
            color_type = ihdr_data["color_type"]
            print("PLTE metadata: " + str(parse_PLTE(chunk, color_type)))
    
    if idat_data and ihdr_data:
        width = ihdr_data["width"]
        height = ihdr_data["height"]
        bit_depth = ihdr_data["bit_depth"]
        color_type = ihdr_data["color_type"]
        idat_data = parse_IDAT(idat_data, width, height, bit_depth, color_type)
        print("IDAT metadata: " + str(idat_data))

def parse_IHDR(chunk):
    if(chunk.type != "IHDR"):
        raise ValueError("Chunk is not type of IHDR")

    fields = struct.unpack(">IIBBBBB", chunk.data)
    ihdr_info = {
        "width": fields[0],
        "height": fields[1],
        "bit_depth": fields[2],
        "color_type": fields[3],
        "compression": fields[4],
        "filter": fields[5],
        "interlace": fields[6]
    }

    return ihdr_info
    
def parse_tEXt(chunk):
    if(chunk.type != "tEXt"):
        raise ValueError("Chunk is not type of tEXt")

    null_pos = chunk.data.find(b'\x00')
    keyword = chunk.data[:null_pos].decode('latin1')
    text = chunk.data[null_pos+1:].decode('latin1')

    return {"keyword": keyword, "text": text}
    
def parse_iTXt(chunk):
    if(chunk.type != "iTXt"):
        raise ValueError("Chunk is not type of iTXt")

    parts = chunk.data.split(b'\x00', 5)
    if len(parts) < 6:
        return None
    
    keyword = parts[0].decode('latin1')
    compression_flag = parts[1]
    compression_method = parts[2]
    language_tag = parts[3].decode('latin1')
    translated_keyword = parts[4].decode('utf-8', errors='ignore')
    text = parts[5]

    if compression_flag == b'\x01':
        text = zlib.decompress(text).decode('utf-8')
    else:
        text = text.decode('utf-8')

    return {
        "keyword": keyword,
        "language": language_tag,
        "translated_keyword": translated_keyword,
        "text": text
    }
    
def parse_tIME(chunk):
    if(chunk.type != "tIME"):
        raise ValueError("Chunk is not type of tIME")

    year, month, day, hour, minute, second = struct.unpack(">HBBBBB", chunk.data)

    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second
    }

def parse_eXIf(chunk):
    if chunk.type != "eXIf":
        raise ValueError("Chunk is not type of eXIf")
    
    try:
        exif_dict = piexif.load(chunk.data)
        readable_exif = {}

        for ifd in exif_dict:
            if isinstance(exif_dict[ifd], dict):
                for tag in exif_dict[ifd]:
                    tag_name = piexif.TAGS[ifd][tag]["name"]
                    readable_exif[tag_name] = exif_dict[ifd][tag]

        return readable_exif

    except Exception as e:
        print(f"Error parsing EXIF: {e}")
        return None

def parse_zTXt(chunk):
    if(chunk.type != "zTXt"):
        raise ValueError("Chunk is not type of zTXt")

    null_pos = chunk.data.find(b'\x00')
    keyword = chunk.data[:null_pos].decode('latin1')
    compression_method = chunk.data[null_pos + 1]
    compressed_text = chunk.data[null_pos + 2:]

    if compression_method != 0:
        raise ValueError("Unsupported compression method in zTXt")

    text = zlib.decompress(compressed_text).decode('latin1')

    return {"keyword": keyword, "text": text}

def parse_pHYs(chunk):
    if(chunk.type != "pHYs"):
        raise ValueError("Chunk is not type of pHYs")
    
    pixels_per_unit_X, pixels_per_unit_Y, unit_sepecifier = struct.unpack(">IIB", chunk.data)

    unit = "meter" if unit_sepecifier == 1 else "unknown"   

    return {
        "pixels_per_unit_X": pixels_per_unit_X,
        "pixels_per_unit_Y": pixels_per_unit_Y,
        "unit_sepecifier": unit
    }

def parse_PLTE(chunk, color_type):
    if chunk.type != "PLTE":
        raise ValueError("Chunk is not type of PLTE")

    if color_type == 0 or color_type == 4:
        raise ValueError("PLTE chunk must not appeare for this image")

    data = chunk.data
    if len(data) % 3 != 0:
        raise ValueError("PLTE chunk length is not divisible by 3.")

    palette = []
    for i in range(0, len(data), 3):
        r = data[i]
        g = data[i+1]
        b = data[i+2]
        palette.append((r, g, b))

    return {
        "colors_count": len(palette),
        "colors": palette
    }

def paeth_predictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

def undo_filter(filter_type, scanline, prev_scanline, bytes_per_pixel):
    result = bytearray(len(scanline))
    if filter_type == 0:  # None
        return scanline
    elif filter_type == 1:  # Sub
        for i in range(len(scanline)):
            left = result[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
            result[i] = (scanline[i] + left) & 0xFF
    elif filter_type == 2:  # Up
        for i in range(len(scanline)):
            up = prev_scanline[i] if prev_scanline else 0
            result[i] = (scanline[i] + up) & 0xFF
    elif filter_type == 3:  # Average
        for i in range(len(scanline)):
            left = result[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
            up = prev_scanline[i] if prev_scanline else 0
            result[i] = (scanline[i] + ((left + up) // 2)) & 0xFF
    elif filter_type == 4:  # Paeth
        for i in range(len(scanline)):
            left = result[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
            up = prev_scanline[i] if prev_scanline else 0
            up_left = prev_scanline[i - bytes_per_pixel] if (prev_scanline and i >= bytes_per_pixel) else 0
            result[i] = (scanline[i] + paeth_predictor(left, up, up_left)) & 0xFF
    else:
        raise ValueError(f"Unknown filter type {filter_type}")
    return result

def get_dominant_colors(arr, color_type, top_n=5):
    if color_type == 3:
        flat = arr.flatten()
        return {f"Palette index {k}": v for k, v in Counter(flat).most_common(top_n)}
    elif color_type in (2, 6):
        pixels = arr.reshape(-1, arr.shape[-1])[:, :3]
        pixels = [(int(p[0]), int(p[1]), int(p[2])) for p in pixels]
        color_counts = Counter(pixels)
        return {f"RGB{color}": count for color, count in color_counts.most_common(top_n)}
    return None

def get_compression_info(idat_data):
    original_size = len(idat_data)
    decompressed = zlib.decompress(idat_data)
    ratio = original_size / len(decompressed)
    return {
        "compressed_size": original_size,
        "uncompressed_size": len(decompressed),
        "compression_ratio": round(ratio, 2)
    }

def has_transparency(arr, color_type):
    if color_type not in (4, 6):
        return False
    alpha_channel = arr[..., -1] if color_type == 6 else arr[..., 1]
    if np.any(alpha_channel < 255):
        return True
    return False

def get_image_stats(arr, color_type):
    stats = {
        "min_value": float(np.min(arr)),
        "max_value": float(np.max(arr)),
        "mean_value": float(np.mean(arr)),
        "std_dev": float(np.std(arr)),
        "unique_values": len(np.unique(arr)) if color_type == 3 else None
    }
    
    if color_type in (2, 6):  # RGB/RGBA
        stats["channel_stats"] = {
            "R": {"min": float(np.min(arr[..., 0])), "max": float(np.max(arr[..., 0]))},
            "G": {"min": float(np.min(arr[..., 1])), "max": float(np.max(arr[..., 1]))},
            "B": {"min": float(np.min(arr[..., 2])), "max": float(np.max(arr[..., 2]))}
        }
        if color_type == 6:  # RGBA
            stats["channel_stats"]["A"] = {
                "min": float(np.min(arr[..., 3])),
                "max": float(np.max(arr[..., 3]))
            }
    
    return stats

def parse_IDAT(idat_data, width, height, bit_depth, color_type):
    try:
        decompressed = zlib.decompress(idat_data)
    except zlib.error as e:
        raise ValueError(f"Decompression failed: {e}")

    if color_type == 0:  # Grayscale
        channels = 1
    elif color_type == 2:  # RGB
        channels = 3
    elif color_type == 3:  # Indexed
        channels = 1
    elif color_type == 4:  # Grayscale + Alpha
        channels = 2
    elif color_type == 6:  # RGBA
        channels = 4
    else:
        raise ValueError(f"Unsupported color type: {color_type}")

    bits_per_scanline = width * channels * bit_depth
    bytes_per_scanline = (bits_per_scanline + 7) // 8

    pixels = []
    prev_scanline = None
    offset = 0
    
    for _ in range(height):
        if offset + 1 + bytes_per_scanline > len(decompressed):
            raise ValueError("Unexpected end of IDAT data")

        filter_type = decompressed[offset]
        offset += 1
        
        scanline = decompressed[offset:offset + bytes_per_scanline]
        offset += bytes_per_scanline

        unfiltered = undo_filter(filter_type, scanline, prev_scanline, (channels * bit_depth + 7) // 8)
        pixels.append(unfiltered)
        prev_scanline = unfiltered

    pixel_data = b''.join(pixels)

    if bit_depth == 8:
        dtype = np.uint8
    elif bit_depth == 16:
        dtype = '>u2'
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")

    arr = np.frombuffer(pixel_data, dtype=dtype)

    if color_type in (2, 6):  # RGB/RGBA
        arr = arr.reshape((height, width, channels))
    elif color_type in (0, 3, 4):  # Grayscale/Indexed/Grayscale+Alpha
        if channels > 1:
            arr = arr.reshape((height, width, channels))
        else:
            arr = arr.reshape((height, width))

    metadata = {
        "stats": get_image_stats(arr, color_type),
        "dominant_colors": get_dominant_colors(arr, color_type),
        "compression": get_compression_info(idat_data),
        "raw_shape": f"{height}x{width}x{channels}",
        "has_transparency": has_transparency(arr, color_type)
    }

    return metadata

def write_chunks(filename, chunks):
    with open(filename, "wb") as f:
        f.write(PNG_SIGNATURE)

        for chunk in chunks:
            f.write(chunk.length.to_bytes(4, "big"))
            f.write(chunk.type.encode("ascii"))
            f.write(chunk.data)
            f.write(chunk.crc.to_bytes(4, "big"))