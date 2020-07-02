# 2020 Tarpeeksi Hyvae Soft
# Software: pfm-view

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QScroller
from PyQt5.QtGui import QImage, QColor, QPixmap
from .pfm_image import PFMImage

app = None
mainWindow = None

def run(cliArguments):
    """Creates and displays the app's main window. The window's event loop will
    run until the user requests to close the window, at which point the whole
    script will exit."""

    global app, mainWindow

    app = QApplication(cliArguments)
    mainWindow = uic.loadUi("./src/pfm_view/main_window.ui")

    mainWindow.actionLoad_PFM.triggered.connect(__load_pfm_file)
    mainWindow.actionExit.triggered.connect(lambda: app.exit(0))

    # Allow click + drag to scroll.
    QScroller.grabGesture(mainWindow.scrollArea.viewport(), QScroller.LeftMouseButtonGesture)

    mainWindow.show()
    sys.exit(app.exec())

def __qimage_from_pfm_image(pfmImage:PFMImage, tonemapping:str = "flat"):
    """Converts the given PFM image into a QImage, and returns the result. The
    conversion includes tonemapping the converted image's pixels."""

    qimage = QImage(pfmImage.width, pfmImage.height, QImage.Format_RGB32)

    assert (tonemapping == "flat"),\
           "Only flat tonemapping is supported at this time."

    # Flat tonemapping finds the largest pixel value in the image, then scales
    # all pixels by that value such that the brightest value becomes 1.
    if tonemapping == "flat":
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
                qimage.setPixelColor(x, y, QColor(max(0, min(255, ((color["red"] / maxValue)  * 255))),
                                                  max(0, min(255, ((color["green"] / maxValue) * 255))),
                                                  max(0, min(255, ((color["blue"] / maxValue)  * 255)))))

    return qimage

def __display_qimage(image:QImage):
    """Paints the given QImage onto the GUI's image dispay area."""

    mainWindow.setMaximumSize(image.width(), (image.height() + mainWindow.menuBar.height()))
    mainWindow.imageDisplay.setPixmap(QPixmap.fromImage(image))

def __load_pfm_file():
    """Asks the user to specify a PFM file to load, then loads it and displays it
    in the GUI's image display area."""

    filename = QFileDialog.getOpenFileName(mainWindow,
                                           "Select a PFM file to load",
                                           ".",
                                           "*.pfm")[0]
    
    if not filename:
        return
    
    # TODO: Add a progress bar for while the data is being loaded.
    pfm = PFMImage(filename)
    qimage = __qimage_from_pfm_image(pfm)

    __display_qimage(qimage)