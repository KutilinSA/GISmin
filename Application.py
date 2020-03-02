from PyQt5.QtWidgets import QApplication
from UI.UI import UI
import sys


class Application:
    def __init__(self, args):
        args.append("--disable-web-security")
        self.app = QApplication(args)
        self.ui = UI()

    def run(self):
        sys.exit(self.app.exec_())

