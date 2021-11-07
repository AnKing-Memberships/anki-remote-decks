import base64

import aqt

from .. import config
from ..parse_classes.ParsedDeck import ParsedDeck
from ..note_dict_from_parsed_note import note_dict_from_parsed_note
from .AnkiBridge import AnkiBridge


class AnkiPluginConnector:
    def __init__(self, rootDeck=config.rootDeck):
        self.AnkiBridge = AnkiBridge()
        self.root_deck = rootDeck

    def create_new_deck(self, deck: ParsedDeck):

        self._buildNewDecksAsRequired(deck.getDeckNames())

        # Add notes
        for note in deck.get_notes():
            self.addNote(note)

        # Add media
        media = self.prepareMedia(deck.getMedia())
        for media_info in media:
            self.AnkiBridge.storeMediaFile(
                media_info.get("fileName"), media_info.get("data")
            )

    def prepareMedia(self, ankiMedia):  # ([])

        formattedMedia = []
        if len(ankiMedia) == 0:
            return formattedMedia
        else:
            for i in ankiMedia:
                if self.AnkiBridge.checkForMediaFile(i.fileName) == False:
                    if i.lazyLoad == True:
                        i.lazyLoadImage()
                    formattedMedia.append(
                        {
                            "fileName": i.fileName,
                            "data": base64.b64encode(i.data).decode("utf-8"),
                        }
                    )
        return formattedMedia

    def _buildNewDecksAsRequired(self, deck_names):
        new_deck_paths = []
        for deck_name in deck_names:
            full_deck_path = self._getFullDeckPath(deck_name)
            if (
                full_deck_path not in self.AnkiBridge.deckNames()
                and full_deck_path not in new_deck_paths
            ):
                new_deck_paths.append(full_deck_path)

        # Create decks
        for deck in new_deck_paths:
            self.AnkiBridge.createDeck(deck)

    def _getFullDeckPath(self, deckName):  # (str)
        if self.root_deck == None:
            return str(deckName)
        else:
            return str(self.root_deck + "::" + deckName)

    def getDeckNotes(self, deckName):
        # TODO => revisit return type
        return self.AnkiBridge.getDeckNotes(deckName)

    def addNote(self, note):
        note_dict = note_dict_from_parsed_note(note, self.root_deck)
        self.AnkiBridge.addNote(note_dict)

    def deleteNotes(self, noteIds):
        self.AnkiBridge.deleteNotes(noteIds)

    def updateNoteFields(self, note):

        # TODO ensure note is logically correct
        self.AnkiBridge.updateNoteFields(note)

    def getConfig(self):
        return aqt.mw.addonManager.getConfig(__name__)

    def writeConfig(self, config):
        aqt.mw.addonManager.writeConfig(__name__, config)

    def checkForMediaFile(self, filename):
        return self.AnkiBridge.checkForMediaFile(filename)

    def startEditing(self):
        self.AnkiBridge.startEditing()

    def stopEditing(self):
        self.AnkiBridge.stopEditing()
