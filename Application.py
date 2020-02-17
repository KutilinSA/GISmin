from PyQt5.QtWidgets import QApplication
from UI.UI import UI
import sys


class Application:
    def __init__(self):
        self.app = QApplication([])
        self.ui = UI()

    def run(self):
        sys.exit(self.app.exec_())


app = Application()
app.run()
