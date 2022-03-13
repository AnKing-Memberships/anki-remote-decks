from aqt import mw
from aqt.gui_hooks import profile_did_open
from aqt.qt import *
from aqt.utils import showInfo

from .compat import add_compat_aliases
from .gui.menu import setup_menu
from .libs.org_to_anki.ankiConnectWrapper.AnkiPluginConnector import AnkiPluginConnector
from .main import add_new_deck, remove_remote_deck, sync_decks

CONFIG = mw.addonManager.getConfig(__name__)

errorTemplate = """
Hey there! It seems an error has occurred while using the <b>Remote Decks</b> add-on.<br>
<br>
The error was:<br>
<i>{}</i><br>
<br>
If you would like me to fix it please report it here: <a href="https://github.com/AnKingMed/anki-remote-decks/issues">https://github.com/AnKingMed/anki-remote-decks/issues</a><br> 
<br>
Please be sure to provide as much information as possible. Specifically the file that caused the error.<br>
(Another window with an error message will open after you close this)
"""


def addDeck():

    try:
        ankiBridge = AnkiPluginConnector()
        ankiBridge.startEditing()
        add_new_deck()

    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage), textFormat="rich")
        raise e

    finally:
        ankiBridge.stopEditing()
        mw.reset()


def syncDecks():

    try:
        ankiBridge = AnkiPluginConnector()
        ankiBridge.startEditing()
        sync_decks()

    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage), textFormat="rich")
        raise e

    finally:
        showInfo("Sync completed")
        ankiBridge.stopEditing()
        mw.reset()


def removeRemote():

    try:
        ankiBridge = AnkiPluginConnector()
        ankiBridge.startEditing()
        remove_remote_deck()

    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage), textFormat="rich")
        raise e

    finally:
        ankiBridge.stopEditing()
        mw.reset()


menu = setup_menu()

remoteDeckAction = QAction("Add new remote Deck", mw)
remoteDeckAction.setShortcut(QKeySequence(CONFIG["add_deck_shortcut"]))
remoteDeckAction.triggered.connect(addDeck)
menu.addAction(remoteDeckAction)

syncDecksAction = QAction("Sync remote decks", mw)
syncDecksAction.setShortcut(QKeySequence(CONFIG["sync_shortcut"]))
syncDecksAction.triggered.connect(syncDecks)
menu.addAction(syncDecksAction)

removeRemoteDeck = QAction("Remove remote deck", mw)
removeRemoteDeck.setShortcut(QKeySequence(CONFIG["remove_deck_shortcut"]))
removeRemoteDeck.triggered.connect(removeRemote)
menu.addAction(removeRemoteDeck)


profile_did_open.append(add_compat_aliases)
