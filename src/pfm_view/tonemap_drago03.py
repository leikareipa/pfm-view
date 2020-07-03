# 2020 Tarpeeksi Hyvae Soft
# Software: pfm-view

# Code adapted with superficial modifications into Python by Tarpeeksi Hyvae
# Soft 2020 from a sample implementation in C by Frédéric Drago 2003. Drago's
# implementation accompanied the paper "Adaptive logarithmic mapping for
# displaying high contrast scenes" (Drago, Myszkowski, Annen & Chiba 2003).
# The original source of Drago's code could no longer be located; the code
# also mentions the following:
#
#     "Great thanks to Erik Reinhard, the implementation of the logmapping
#      tone mapping was started from his framework posted online."
#
# In-code comments have been retained from the original.
#

import math

epsilon = 0.000001

# Convert double floating point RGB data to Yxy, return max and min luminance
# and absolute value of luminance log average for automatic exposure.
def __rgb_Yxy(width, height, pixels):
    global epsilon

    result = ([0] * 3)
    sumVal = 0.0
    array_size = (width * height)

    RGB2Yxy = [[0.5141364, 0.3238786, 0.16036376],
               [0.265068, 0.67023428, 0.06409157],
               [0.0241188, 0.1228178, 0.84442666]]

    maxVal = epsilon
    minVal = math.inf

    for x in range(array_size):
        result[0] = result[1] = result[2] = 0.0

        for i in range(3):
            result[i] += RGB2Yxy[i][0] * pixels[x]["red"]
            result[i] += RGB2Yxy[i][1] * pixels[x]["green"]
            result[i] += RGB2Yxy[i][2] * pixels[x]["blue"]
    
        W = (result[0] + result[1] + result[2])

        if W > 0.0:
            pixels[x]["red"] = result[1]         # Y
            pixels[x]["green"] = (result[0] / W) # x
            pixels[x]["blue"] = (result[1] / W)	 # y
        else:
            pixels[x]["red"] = pixels[x]["green"] = pixels[x]["blue"] = 0.0
    
        maxVal = pixels[x]["red"] if (maxVal < pixels[x]["red"]) else maxVal	# Max Luminance in Scene
        minVal = pixels[x]["red"] if (minVal > pixels[x]["red"]) else minVal	# Min Luminance in Scene
        sumVal += math.log(2.3e-5 + pixels[x]["red"]) # Contrast constant Tumblin paper

    return [maxVal, minVal, (sumVal / (width * height))]

# Convert Yxy image back to double floating point RGB
def __Yxy_rgb(width, height, pixels):
    global epsilon

    result = ([0] * 3)
    array_size = (width * height)

    Yxy2RGB = [[2.5651, -1.1665, -0.3986],
               [-1.0217, 1.9777, 0.0439],
               [0.0753, -0.2543, 1.1892]]

    for x in range(array_size):
        Y = pixels[x]["red"]	        # Y
        result[1] = pixels[x]["green"]  # x
        result[2] = pixels[x]["blue"]	# y

        if (Y > epsilon) and (result[1] > epsilon) and (result[2] > epsilon):
            X = ((result[1] * Y) / result[2])
            Z = ((X / result[1]) - X - Y)
        else:
            X = Z = epsilon

        pixels[x]["red"] = X
        pixels[x]["green"] = Y
        pixels[x]["blue"] = Z

        result[0] = result[1] = result[2] = 0.0

        for i in range(3):
            result[i] += Yxy2RGB[i][0] * pixels[x]["red"]
            result[i] += Yxy2RGB[i][1] * pixels[x]["green"]
            result[i] += Yxy2RGB[i][2] * pixels[x]["blue"]

        pixels[x]["red"] = result[0]
        pixels[x]["green"] = result[1]
        pixels[x]["blue"] = result[2]

def __logmapping(width, height, pixels, Lum_max, Lum_min, world_lum,
                 biasParam, contParam, exposure, white):
    global epsilon

    # Arbitrary Bias Parameter
    if not biasParam:
        biasParam = 0.85

    exp_adapt = 1
    av_lum = (math.exp(world_lum) / exp_adapt)
    biasP = (math.log(biasParam) / math.log(0.5))
    Lmax = (Lum_max / av_lum)
    divider = math.log10(Lmax + 1)

    for x in range(height):
        for y in range(width):
            index = (x * width + y)

            # inverse gamma function to enhance contrast
            # Not in paper
            if contParam:
                pixels[index]["red"] = math.pow(pixels[index]["red"], (1 / contParam))

            pixels[index]["red"] /= av_lum

            if exposure != 1.0:
                pixels[index]["red"] *= exposure

            interpol = math.log(2 + math.pow((pixels[index]["red"] / Lmax), biasP) * 8)

            pixels[index]["red"] = ((math.log(pixels[index]["red"] + 1) / interpol) / divider)

def tonemap_drago03(width, height, pixels, bias = 0.85, exposure = 0):
    """Applies tonemapping as described in Drago, Myszkowski, Annen & Chiba 2003:
    Adaptive logarithmic mapping for displaying high contrast scenes.

    Expects 'pixels' to be a list of pixels in which each element is a dictionary
    containing the properties 'red', 'green', and 'blue'; and for 'width' and
    'height' to give the dimensions of the pixel array."""

    global epsilon

    contrastParam = 0        # Contrast improvement.
    white         = 1.0      # Maximum display luminance.
    exposure      = math.pow(2, exposure)

    [maxLuminance, minLuminance, worldLuminance] = __rgb_Yxy(width, height, pixels)
    __logmapping(width, height, pixels, maxLuminance, minLuminance, worldLuminance, bias, contrastParam, exposure, white)
    __Yxy_rgb(width, height, pixels)
