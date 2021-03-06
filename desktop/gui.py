import sys
import os
import glob
import time
import datetime
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from PIL import Image
reload(sys)
sys.setdefaultencoding("utf-8")


COLORS = matplotlib.rcParams["axes.color_cycle"]


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle("Labeler")

        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s "
                            "- %(message)s", datefmt="%Y/%m/%d %H:%M:%S",
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.axes = []
        self.images = []

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.logger.info("Initialization done.")

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.fig = Figure((8.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.open_button = QPushButton("Open")
        self.connect(self.open_button, SIGNAL('clicked()'), self.on_open)

        self.label_button_1 = QPushButton("&Label 1")
        self.connect(self.label_button_1, SIGNAL('clicked()'), self.on_label_1)

        self.label_button_2 = QPushButton("&Label 2")
        self.connect(self.label_button_2, SIGNAL('clicked()'), self.on_label_2)

        hbox = QHBoxLayout()

        for w in [self.open_button, self.label_button_1, self.label_button_2]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        main_layout = QHBoxLayout()
        main_layout.addLayout(vbox)

        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("&File"))

        quit_action = self.create_action(
            self.tr("&Quit"), slot=self.close, shortcut="Ctrl+Q",
            tip=self.tr("Close the application"))

        self.add_actions(self.file_menu, (quit_action,))

    def create_status_bar(self):
        self.status_text = QLabel("")
        self.statusBar().addWidget(self.status_text, 1)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                      tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def on_open(self):
        files = glob.glob("data/*.jpg")
        number = int(len(files))
        rows = int(np.sqrt(number))
        cols = number // rows
        if number % cols > 0:
            cols += 1
        self.logger.debug("Loading %d images" % number)
        for ax in self.axes:
            self.fig.delaxes(ax)
        self.axes = []
        self.images = []
        for n in range(number):
            ax = self.fig.add_subplot(cols, rows, n + 1)
            ax.set_xticks(())
            ax.set_yticks(())
            image = np.asarray(Image.open(files[n]))
            self.logger.debug("Loading image %d" % (n + 1))
            ax.imshow(image)
            self.axes.append(ax)
            self.images.append(image)
        self.canvas.draw()

    def on_label_1(self):
        self.on_label(0)

    def on_label_2(self):
        self.on_label(1)

    def on_label(self, label):
        self.logger.debug("Label %d" % label)
        timestamp = "%d" % time.time()
        np.save("data/%s.npy" % timestamp, self.images[0])
        f = open("data/labels.txt", "a")
        f.write(timestamp + " " + str(label) + "\n")


def main():
    app = QApplication(sys.argv)
    locale = QLocale.system().name()
    qt_translator = QTranslator()
    if qt_translator.load("qt_" + locale):
        app.installTranslator(qt_translator)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
