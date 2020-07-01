#!/usr/bin/env python3

from pathlib import Path

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
pfmPixels = b"\x0a".join(pfmConstituents[3:])

print(pfmType, pfmWidth, pfmHeight, pfmIsLittleEndian, len(pfmPixels))
