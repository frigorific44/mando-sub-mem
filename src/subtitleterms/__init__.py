# import the main window object (mw) from aqt
import os
import sys

from aqt import mw
from aqt.qt import QAction

# import the "show info" tool from utils.py
from aqt.utils import qconnect

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "vendor")
sys.path.append(vendor_dir)

from .ui import ImportDialog  # noqa: E402

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.


def testFunction() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    # cardCount = mw.col.card_count()
    # show a message box
    # showInfo("Card count: %d" % cardCount)
    ImportDialog().getSettings()


# create a new menu item, "test"
action = QAction("AnkiSub: Import from Subbed", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, testFunction)
mw.form.menuCol.insertAction(mw.form.menuCol.actions()[-1], action)
