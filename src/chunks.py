class PngChunk:
    def __init__(self, length, chunk_type, data, crc):
        self.length = length
        self.type = chunk_type
        self.data = data
        self.crc = crc

    def __str__(self):
        return f"Chunk {self.type} ({self.length} bytes)"
