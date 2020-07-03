# 2020 Tarpeeksi Hyvae Soft
# Software: pfm-view

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QScroller, QActionGroup
from PyQt5.QtGui import QImage, QColor, QPixmap
from .pfm_image import PFMImage
from .tonemap_drago03 import tonemap_drago03

app = None
mainWindow = None
pfmImage = None           # The PFM image we're currently displaying.
tonemappingModel = "None" # The tone mapping model to apply to the PFM image for displaying it.

def run(cliArguments):
    """Creates and displays the app's main window. The window's event loop will
    run until the user requests to close the window, at which point the whole
    script will exit."""

    global app, mainWindow

    app = QApplication(cliArguments)
    mainWindow = uic.loadUi("./src/pfm_view/main_window.ui")

    mainWindow.actionLoad_PFM.triggered.connect(__load_pfm_file)
    mainWindow.actionExit.triggered.connect(lambda: app.exit(0))

    tonemapGroup = QActionGroup(mainWindow.menuTonemap)
    mainWindow.actionTonemapNone.setActionGroup(tonemapGroup)
    mainWindow.actionTonemapLinear.setActionGroup(tonemapGroup)
    mainWindow.actionTonemapDrago03.setActionGroup(tonemapGroup)
    mainWindow.actionTonemapNone.triggered.connect(lambda: __set_tonemapping_model("None"))
    mainWindow.actionTonemapLinear.triggered.connect(lambda: __set_tonemapping_model("Linear"))
    mainWindow.actionTonemapDrago03.triggered.connect(lambda: __set_tonemapping_model("Drago '03"))
    mainWindow.actionTonemapDrago03.trigger() # Set as the default option.

    # Allow click + drag to scroll.
    QScroller.grabGesture(mainWindow.scrollArea.viewport(), QScroller.LeftMouseButtonGesture)

    mainWindow.show()
    sys.exit(app.exec())

def __set_tonemapping_model(model:str):
    global tonemappingModel

    tonemappingModel = model

    # If we have a PFM image loaded, refresh it with the new tonemapping model.
    if pfmImage:
        __display_pfm_image(pfmImage, tonemappingModel)

def __qimage_from_pfm_image(pfmImage:PFMImage, tonemappingModel:str):
    """Converts the given PFM image into a QImage, and returns the result. The
    conversion includes tonemapping the converted image's pixels."""

    qimage = QImage(pfmImage.width, pfmImage.height, QImage.Format_RGB32)

    if tonemappingModel == "None":
        for y in range(pfmImage.height):
            for x in range(pfmImage.width):
                color = pfmImage.color_at(x, y)
                qimage.setPixelColor(x, y, QColor(max(0, min(255, color["red"]   * 255)),
                                                  max(0, min(255, color["green"] * 255)),
                                                  max(0, min(255, color["blue"]  * 255))))
    # Linear tonemapping finds the largest pixel value in the image, then scales
    # all pixels by that value such that the brightest value becomes 1.
    elif tonemappingModel == "Linear":
        maxValue = 0
        for y in range(pfmImage.height):
            for x in range(pfmImage.width):
                pixelColor = pfmImage.color_at(x, y)
                maxValue = max(maxValue, pixelColor["red"])
                maxValue = max(maxValue, pixelColor["green"])
                maxValue = max(maxValue, pixelColor["blue"])

        for y in range(pfmImage.height):
            for x in range(pfmImage.width):
                color = pfmImage.color_at(x, y)
                qimage.setPixelColor(x, y, QColor(max(0, min(255, (color["red"]   / maxValue) * 255)),
                                                  max(0, min(255, (color["green"] / maxValue) * 255)),
                                                  max(0, min(255, (color["blue"]  / maxValue) * 255))))
    elif tonemappingModel == "Drago '03":
        tonemappedPixels = []

        for y in range(pfmImage.height):
            for x in range(pfmImage.width):
                pixelColor = pfmImage.color_at(x, y)
                tonemappedPixels.append({
                    "red": pixelColor["red"],
                    "green": pixelColor["green"],
                    "blue": pixelColor["blue"]
                })

        tonemap_drago03(pfmImage.width, pfmImage.height, tonemappedPixels)

        for y in range(pfmImage.height):
            for x in range(pfmImage.width):
                color = tonemappedPixels[x + y * pfmImage.width]
                qimage.setPixelColor(x, y, QColor(max(0, min(255, (color["red"]   * 255))),
                                                  max(0, min(255, (color["green"] * 255))),
                                                  max(0, min(255, (color["blue"]  * 255)))))
    else:
        raise AssertionError("Unrecognized tonemapping mode.")

    return qimage

def __display_pfm_image(pfmImage:PFMImage, tonemappingModel:str):
    """Paints the given PFM image onto the GUI's image dispay area."""

    qimage = __qimage_from_pfm_image(pfmImage, tonemappingModel)

    mainWindow.setMaximumSize(qimage.width(), (qimage.height() + mainWindow.menuBar.height()))
    mainWindow.imageDisplay.setPixmap(QPixmap.fromImage(qimage))

def __load_pfm_file():
    """Asks the user to specify a PFM file to load, then loads it and displays it
    in the GUI's image display area."""

    global pfmImage, tonemappingModel

    filename = QFileDialog.getOpenFileName(mainWindow,
                                           "Select a PFM file to load",
                                           ".",
                                           "*.pfm")[0]
    
    if not filename:
        return
    
    # TODO: Add a progress bar for while the data is being loaded.
    pfmImage = PFMImage(filename)
    __display_pfm_image(pfmImage, tonemappingModel)
