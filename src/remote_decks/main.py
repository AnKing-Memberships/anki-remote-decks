import sys

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .diffAnkiDecks import diffAnkiDecks
from .libs.org_to_anki.build_note import built_note
from .libs.org_to_anki.utils import getAnkiPluginConnector
from .parseRemoteDeck import getRemoteDeck

remoteDefaultDeck = "Remote Decks"


def syncDecks():

    # Get all remote decks from config
    ankiBridge = getAnkiPluginConnector(remoteDefaultDeck)

    baseDeck = ankiBridge.defaultDeck
    deckJoiner = "::"

    # Get config data
    remote_data = ankiBridge.getConfig()

    # To by synced later
    all_deck_media = []

    for deckKey in remote_data["remote-decks"].keys():
        try:
            current_remote_info = remote_data["remote-decks"][deckKey]

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
            deck_name = baseDeck + deckJoiner + deck_name
            local_deck = ankiBridge.getDeckNotes(deck_name)

            # Local deck has no cards
            if local_deck == []:
                ankiBridge.addCardsToEmptyDeck(remote_deck)
                showInfo("Adding cards to empty deck: {}".format(deck_name))
            else:
                # Diff decks and sync
                deckDiff = diffAnkiDecks(remote_deck, local_deck)
                _sync_new_data(deckDiff)
        except Exception as e:
            deckMessage = "\nThe following deck failed to sync: {}".format(
                deck_name)
            raise type(e)(
                str(e) + deckMessage).with_traceback(sys.exc_info()[2])

    # Sync missing media data
    formattedMedia = ankiBridge.prepareMedia(all_deck_media)

    # Add Media
    # TODO This need to be refactored back into org_to_anki
    for i in formattedMedia:
        ankiBridge.AnkiBridge.storeMediaFile(i.get("fileName"), i.get("data"))


def _sync_new_data(deck_diff):

    ankiBridge = getAnkiPluginConnector(remoteDefaultDeck)

    new_notes = deck_diff["new_notes"]
    updated_notes = deck_diff["updated_notes"]
    removed_notes = deck_diff["removed_notes"]

    # Add new notes
    duplicateQuestion = 0
    for note_info in new_notes:
        note, _ = note_info
        try:
            ankiBridge.addNote(note)
        except Exception as e:
            if e.args[0] == "cannot create note because it is a duplicate":
                duplicateQuestion += 1
            else:
                raise e

    # Update existing notes
    for note_info in updated_notes:
        note, note_id = note_info
        built_note_ = built_note(note)
        _update_note(note_id, built_note_)

    # Remove notes
    for note_info in removed_notes:
        note, note_id = note_info
        ankiBridge.deleteNotes([note_id])


def _update_note(noteId, built_note):
    fields = built_note["fields"]
    ankiNote = mw.col.getNote(noteId)
    if ankiNote is None:
        raise Exception('note was not found: {}'.format(noteId))

    for name, value in fields.items():
        if name in ankiNote:
            ankiNote[name] = value
    ankiNote.tags = built_note["tags"]
    ankiNote.flush()


def addNewDeck():

    # Get url from user
    # url = "https://docs.google.com/document/d/e/2PACX-1vRXWGu8WvCojrLqMKsf8dTOWstrO1yLy4-8x5nkauRnMyc4iXrwkwY3BThXHc3SlCYqv8ULxup3QiOX/pub"
    url, okPressed = QInputDialog.getText(
        mw, "Get Remote Deck url", "Remote Deck url:", QLineEdit.Normal, "")
    if okPressed == False:
        return

    # Get data and build deck
    ankiBridge = getAnkiPluginConnector(remoteDefaultDeck)

    deck = getRemoteDeck(url)
    deckName = deck.deckName

    # Add url to user data
    config = ankiBridge.getConfig()

    if config["remote-decks"].get(url, None) != None:
        showInfo("Decks has already been added for: {}".format(url))
        return

    config["remote-decks"][url] = {"url": url, "deckName": deckName}

    # Upload new deck
    ankiBridge.addCardsToEmptyDeck(deck)

    # Update config on success
    ankiBridge.writeConfig(config)


def removeRemoteDeck():

    # Get current remote decks
    ankiBridge = getAnkiPluginConnector(remoteDefaultDeck)

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
        mw, "Select Deck to Unlink", "Select a deck to Unlink", advBasicOptions, 0, False)

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
