#!/usr/bin/env python3

from pathlib import Path
import struct

class Color:
    """RGBA color in the range [0,1] (bounds not enforced)."""

    def __init__(self, red = 1 , green = 0, blue = 1, alpha = 1):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

class PFMImage:
    """Holds data loaded from a PFM image file."""

    def __init__(self, sourceFileName = None):
        self.width = None
        self.height = None
        self.isLittleEndian = None
        self.type = None
        self.userValue = None
        self.pixels = None # Will be a list with a Color element for each pixel.
        self.filename = None

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

        # Convert the binary pixel data into RGB pixel values. Each pixel consists of
        # red, green, and blue channels (no alpha), and each channel is composed of
        # 4 bytes to be interpreted as a 32-bit float.
        pfmPixelBytes = b"\x0a".join(pfmConstituents[3:])
        endianness = ("<f" if self.isLittleEndian else ">f")
        numColorChannels = 3
        bytesPerChannel = 4

        self.pixels = [Color() for x in range(self.width * self.height)]

        for pixelIdx in range(self.width * self.height):

            idxRed   = (pixelIdx * numColorChannels * bytesPerChannel)
            idxGreen = (idxRed + bytesPerChannel)
            idxBlue  = (idxGreen + bytesPerChannel)

            self.pixels[pixelIdx].red   = struct.unpack(endianness, pfmPixelBytes[idxRed:  (idxRed   + bytesPerChannel)])[0]
            self.pixels[pixelIdx].green = struct.unpack(endianness, pfmPixelBytes[idxGreen:(idxGreen + bytesPerChannel)])[0]
            self.pixels[pixelIdx].blue  = struct.unpack(endianness, pfmPixelBytes[idxBlue: (idxBlue  + bytesPerChannel)])[0]

        assert (len(self.pixels) == (self.width * self.height)),\
               "Failed to decode PFM pixel data."

pfm = PFMImage(sourceFileName = "./test.pfm")

print(pfm.filename, pfm.width, pfm.height, pfm.isLittleEndian, pfm.userValue, len(pfm.pixels))
