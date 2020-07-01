#!/usr/bin/env python3

from pathlib import Path
import struct

pfmData = Path("test.pfm").read_bytes()

# A PFM file consists of a header of 3 ASCII lines, followed by a data block
# of all of the image's pixels. Each of the header's ASCII lines is separated
# with a Unix carriage return, and the pixel data block is also separated that
# way from the 3rd ASCII line.
# 
# You can find a more complete description of the PFM format at
# http://www.pauldebevec.com/Research/HDR/PFM/.
#
pfmConstituents = pfmData.split(b"\x0a")
pfmType = pfmConstituents[0].decode("ascii")
[pfmWidth, pfmHeight] = map(lambda binaryValue: int(binaryValue.decode("ascii")), pfmConstituents[1].split(b" "))
pfmIsLittleEndian = (pfmConstituents[2][0] == 45) # 45 representing the ASCII character '-'.
pfmUserValue = abs(float(pfmConstituents[2]))
pfmPixelBytes = b"\x0a".join(pfmConstituents[3:])

print(pfmType, pfmWidth, pfmHeight, pfmIsLittleEndian, pfmUserValue, len(pfmPixelBytes))

class Color:
    """RGBA color in the range [0,1] (bounds not enforced)."""

    def __init__(self, red, green, blue, alpha = 1):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

# Convert the binary pixel data into RGB pixel values. Each pixel consists of
# red, green, and blue channels (no alpha), and each channel is composed of
# 4 bytes to be interpreted as a 32-bit float.
endianness = ("<f" if pfmIsLittleEndian else ">f")
numColorChannels = 3
bytesPerChannel = 4
pfmPixels = []
for pixel in range(pfmWidth * pfmHeight):

    idxRed   = (pixel * numColorChannels * bytesPerChannel)
    idxGreen = (idxRed + bytesPerChannel)
    idxBlue  = (idxGreen + bytesPerChannel)

    pfmPixels.append(Color(red   = struct.unpack(endianness, pfmPixelBytes[idxRed:  (idxRed   + bytesPerChannel)])[0],
                           green = struct.unpack(endianness, pfmPixelBytes[idxGreen:(idxGreen + bytesPerChannel)])[0],
                           blue  = struct.unpack(endianness, pfmPixelBytes[idxBlue: (idxBlue  + bytesPerChannel)])[0]))

assert (len(pfmPixels) == (pfmWidth * pfmHeight)),\
       "Failed to decode PFM pixel data."
