from aqt import mw
from aqt.qt import QDialog, QFileDialog

from .importdialog import Ui_ImportDialog


class ImportDialog(QDialog, Ui_ImportDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        self.setupUi(self)
        self.filePushButton.clicked.connect(self.onBrowse)

    def onBrowse(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if fileDialog.exec():
            filenames = fileDialog.selectedFiles()
            if filenames:
                self.fileLineEdit.setText(filenames[0])
