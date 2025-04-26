from chunks import PngChunk
import struct
import zlib

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
    for chunk in chunks:
        if chunk.type == "IHDR":
            print("IHDR metadata: " + str(parse_IHDR(chunk)))

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
    if(chunk.type != "eXIf"):
        raise ValueError("Chunk is not type of eXIf")

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
