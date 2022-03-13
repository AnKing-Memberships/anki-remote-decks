import sys

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .deck_diff import deck_diff
from .libs.org_to_anki.ankiConnectWrapper.AnkiPluginConnector import AnkiPluginConnector
from .libs.org_to_anki.note_dict_from_parsed_note import note_dict_from_parsed_note
from .parse_remote_deck import getRemoteDeck

# name of the deck that is the root of all remote decks
ROOT_DECK_NAME = "Remote Decks"


def sync_decks():

    # Get all remote decks from config
    ankiBridge = AnkiPluginConnector(ROOT_DECK_NAME)

    # Get config data
    CONFIG = ankiBridge.getConfig()

    # To be synced later
    all_deck_media = []

    for deck_key in CONFIG["remote-decks"].keys():
        try:
            current_remote_info = CONFIG["remote-decks"][deck_key]

            # Get Remote deck
            deck_name = current_remote_info["deckName"]
            remote_deck = getRemoteDeck(current_remote_info["url"])

            # Get media and add to collection
            deck_media = remote_deck.getMedia()
            if deck_media != None:
                all_deck_media.extend(deck_media)

            # Update deckname to one specificed in stored data
            remote_deck.deckName = deck_name

            # Get current deck
            deck_name = f"{ROOT_DECK_NAME}::{deck_name}"
            local_deck = ankiBridge.getDeckNotes(deck_name)

            # Update existing deck or create new one
            if local_deck:
                deckDiff = deck_diff(remote_deck, local_deck)
                _sync_deck(deckDiff, current_remote_info["syncMode"])
            else:
                ankiBridge.create_new_deck(remote_deck)
                showInfo("Adding cards to empty deck: {}".format(deck_name))

        except Exception as e:
            deckMessage = f"\nThe following deck failed to sync: {deck_name}"
            raise type(e)(str(e) + deckMessage).with_traceback(sys.exc_info()[2])

    # Sync missing media data
    formattedMedia = ankiBridge.prepareMedia(all_deck_media)

    # Add Media
    for media_info in formattedMedia:
        ankiBridge.AnkiBridge.storeMediaFile(
            media_info.get("fileName"), media_info.get("data")
        )


def _sync_deck(deck_diff, sync_mode):

    ankiBridge = AnkiPluginConnector(ROOT_DECK_NAME)

    new_notes = deck_diff["new_notes"]
    updated_notes = deck_diff["updated_notes"]
    removed_notes = deck_diff["removed_notes"]

    # Add new notes
    duplicateQuestion = 0
    for parsed_note_and_local_id in new_notes:
        note, _ = parsed_note_and_local_id
        try:
            ankiBridge.addNote(note)
        except Exception as e:
            if e.args[0] == "cannot create note because it is a duplicate":
                duplicateQuestion += 1
            else:
                raise e

    assert sync_mode in ["everything", "added_only"]
    if sync_mode == "everything":
        # Update existing notes
        for parsed_note_and_local_id in updated_notes:
            note, note_id = parsed_note_and_local_id
            built_note_ = note_dict_from_parsed_note(note)
            _update_note(note_id, built_note_)

        # Remove notes
        for parsed_note_and_local_id in removed_notes:
            note, note_id = parsed_note_and_local_id
            ankiBridge.deleteNotes([note_id])


def _update_note(noteId, built_note):
    fields = built_note["fields"]
    ankiNote = mw.col.getNote(noteId)
    if ankiNote is None:
        raise Exception("note was not found: {}".format(noteId))

    for name, value in fields.items():
        if name in ankiNote:
            ankiNote[name] = value
    ankiNote.tags = built_note["tags"]
    ankiNote.flush()


class AddRemoteDeckDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Remote Deck")

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.url_input = QLineEdit()
        self.layout.addRow("Remote Deck url:", self.url_input)

        self.layout.addRow(QLabel("Sync mode:"))

        self.sync_mode = None
        self.button_group = QButtonGroup()
        b0 = QRadioButton("Sync added notes")
        b0.setToolTip(
            "Notes from the Google docs document that are not in the local deck will be added to it."
        )

        def on_b0_clicked():
            self.sync_mode = "added_only"

        b0.clicked.connect(on_b0_clicked)
        self.button_group.addButton(b0)

        b1 = QRadioButton("Sync everything (added, updated and deleted)")
        b1.setToolTip(
            "Local deck will mirror Google docs document.\nLocal changes will be overwritten on sync."
        )

        def on_b1_clicked():
            self.sync_mode = "everything"

        b1.clicked.connect(on_b1_clicked)
        self.button_group.addButton(b1)
        self.layout.addRow(b0)
        self.layout.addRow(b1)

        on_b0_clicked()
        b0.setChecked(True)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addRow(button_box)


def add_new_deck():

    dialog = AddRemoteDeckDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    url = dialog.url_input.text()
    sync_mode = dialog.sync_mode

    # Get data and build deck
    ankiBridge = AnkiPluginConnector()

    deck = getRemoteDeck(url)
    deck_name = deck.deckName

    # Add url to user data
    config = ankiBridge.getConfig()

    if config["remote-decks"].get(url, None) != None:
        showInfo("Decks has already been added for: {}".format(url))
        return

    config["remote-decks"][url] = {
        "url": url,
        "deckName": deck_name,
        "syncMode": sync_mode,
    }

    # Upload new deck
    ankiBridge.create_new_deck(deck)

    # Update config on success
    ankiBridge.writeConfig(config)


def remove_remote_deck():

    # Get current remote decks
    ankiBridge = AnkiPluginConnector()

    config = ankiBridge.getConfig()
    remoteDecks = config["remote-decks"]

    # Get all deck name
    deckNames = []
    for key in remoteDecks.keys():
        deckNames.append(remoteDecks[key]["deckName"])

    if len(deckNames) == 0:
        showInfo("Currently there are no remote decks".format())
        return

    # Ask user to choose a deck
    advBasicOptions = deckNames
    selection, okPressed = QInputDialog.getItem(
        mw,
        "Select Deck to Unlink",
        "Select a deck to Unlink",
        advBasicOptions,
        0,
        False,
    )

    # Remove desk
    if okPressed == True:

        newRemoteDeck = remoteDecks.copy()
        for k in remoteDecks.keys():
            if selection == remoteDecks[k]["deckName"]:
                newRemoteDeck.pop(k)

        config["remote-decks"] = newRemoteDeck
        # Update config on success
        ankiBridge.writeConfig(config)

    return
