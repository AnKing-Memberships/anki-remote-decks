from aqt.qt import QMenu

from .anking_menu import get_anking_menu


def setup_menu() -> None:
    anking_menu = get_anking_menu()
    result = QMenu("Remote Decks")
    anking_menu.addMenu(result)
    return result
