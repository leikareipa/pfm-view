# 2020 Tarpeeksi Hyvae Soft
# Software: pfm-view

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMenuBar, QAction, QMenu, QFileDialog
from .pfm_image import PFMImage

app = None
mainWindow = None

def run(cliArguments):
    global app, mainWindow

    app = QApplication(cliArguments)
    mainWindow = uic.loadUi("./src/pfm_view/main_window.ui")

    mainWindow.actionLoad_PFM.triggered.connect(__load_pfm)
    mainWindow.actionExit.triggered.connect(lambda: app.exit(0))

    mainWindow.show()
    sys.exit(app.exec())

def __load_pfm():
    filename = QFileDialog.getOpenFileName(mainWindow, "Hello", ".", "*.pfm")[0]
    
    if not filename:
        return
    
    pfm = PFMImage(filename)
