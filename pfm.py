#!/usr/bin/env python3

from pathlib import Path
import struct

class PFMImage:
    """Holds data loaded from a PFM image file."""

    # PFM files' pixel data is RGB with each channel being represented by 4
    # bytes (to be interpreted as a 32-bit float).
    NUM_COLOR_CHANNELS = 3
    NUM_BYTES_PER_CHANNEL = 4

    def __init__(self, sourceFileName = None):
        self.width = None
        self.height = None
        self.isLittleEndian = None
        self.type = None
        self.userValue = None
        self.filename = None
        self.rawPixelData = None # The PFM's pixel data as a raw byte array.

        if sourceFileName:
            self.load_from_file(sourceFileName)

    def load_from_file(self, pfmFileName):
        """Populates this instance with data from the given PFM file.
        
        A PFM file consists of a header of 3 ASCII lines, followed by a data block
        of all of the image's pixels. Each of the header's ASCII lines is separated
        with a Unix carriage return, and the pixel data block is also separated that
        way from the 3rd ASCII line.
        
        You can find a more complete description of the PFM format at
        http://www.pauldebevec.com/Research/HDR/PFM/."""

        self.filename = pfmFileName
        pfmData = Path(pfmFileName).read_bytes()
        pfmConstituents = pfmData.split(b"\x0a")

        self.type = pfmConstituents[0].decode("ascii")
        [self.width, self.height] = map(lambda binaryValue: int(binaryValue.decode("ascii")), pfmConstituents[1].split(b" "))
        self.isLittleEndian = (pfmConstituents[2][0] == 45) # 45 representing the ASCII character '-'.
        self.userValue = abs(float(pfmConstituents[2]))
        self.rawPixelData = b"\x0a".join(pfmConstituents[3:])

        numPixels = (len(self.rawPixelData) / (self.NUM_COLOR_CHANNELS * self.NUM_BYTES_PER_CHANNEL))

        assert (numPixels == (self.width * self.height)),\
               "Failed to decode PFM pixel data."

    def color_at(self, x, y):
        """Returns the RGB color of the PFM image at pixel coordinates XY."""
        
        return {
            "red":   self.red_at(x, y),
            "green": self.green_at(x, y),
            "blue":  self.blue_at(x, y),
        }

    def color_channel_value_at(self, x, y, channelIdx = 0):
        """Returns the value of color channel n of the pixel at XY in the PFM image."""

        endianness = ("<f" if self.isLittleEndian else ">f")
        idx = (((x + y * self.width) * self.NUM_COLOR_CHANNELS * self.NUM_BYTES_PER_CHANNEL) + (channelIdx * self.NUM_BYTES_PER_CHANNEL))
        channelValue = struct.unpack(endianness, self.rawPixelData[idx:(idx + self.NUM_BYTES_PER_CHANNEL)])[0]

        return channelValue

    def red_at(self, x, y):
        return self.color_channel_value_at(x, y, 0)

    def green_at(self, x, y):
        return self.color_channel_value_at(x, y, 1)

    def blue_at(self, x, y):
        return self.color_channel_value_at(x, y, 2)


pfm = PFMImage(sourceFileName = "./test.pfm")

print(pfm.filename, pfm.width, pfm.height, pfm.isLittleEndian, pfm.userValue, len(pfm.rawPixelData))
print(pfm.color_at(0, 0))
