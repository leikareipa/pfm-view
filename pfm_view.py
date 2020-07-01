#!/usr/bin/env python3

from src.pfm_view.pfm_image import PFMImage

pfm = PFMImage(sourceFileName = "./test.pfm")

print(pfm.filename, pfm.width, pfm.height, pfm.isLittleEndian, pfm.userValue, len(pfm.rawPixelData))
print(pfm.color_at(0, 0))
