import pathlib
from aqt import mw
from aqt.qt import QDialog, QFileDialog
from aqt.utils import showWarning

from ..deck import decks
from .importdialog import Ui_ImportDialog


class ImportDialog(QDialog, Ui_ImportDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        self.setupUi(self)
        self.filePushButton.clicked.connect(self.onBrowse)
        self.dictionaryComboBox.addItem("-")
        self.dictionaryComboBox.addItems(decks.keys())
        self.exec()

    def onBrowse(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if fileDialog.exec():
            filenames = fileDialog.selectedFiles()
            if filenames:
                self.fileLineEdit.setText(filenames[0])

    def getSettings(self):
        if self.result() == QDialog.rejected:
            return None
        file_path = self.fileLineEdit.text()
        if not file_path:
            showWarning("Please select a file.")
            return None
        if not pathlib.Path(file_path).exists():
            showWarning("File does not exist.")
            return None
        dict_choice = self.dictionaryComboBox.currentText()
        if dict_choice not in decks:
            showWarning("Please select a dictionary.")
            return None
        deck_name = self.nameLineEdit.text()
        if not deck_name:
            showWarning("Please enter a name.")
            return None
        return {"path": file_path, "dict": dict_choice, "name": deck_name}
