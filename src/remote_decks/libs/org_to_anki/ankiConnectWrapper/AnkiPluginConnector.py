import base64

from .. import config
from ..ankiClasses.AnkiDeck import AnkiDeck
from ..build_note_dict import build_note_dict
from .AnkiBridge import AnkiBridge

import aqt


class AnkiPluginConnector:

    def __init__(self, defaultDeck=config.defaultDeck):
        self.AnkiBridge = AnkiBridge()
        self.root_deck = defaultDeck

    def create_new_deck(self, deck: AnkiDeck):

        self._buildNewDecksAsRequired(deck.getDeckNames())

        # Add notes
        note_dicts = [
            build_note_dict(note, self.root_deck)
            for note in deck.get_notes()
        ]
        for note_dict in note_dicts:
            self.AnkiBridge.addNote(note_dict)

        # Add media
        media = self.prepareMedia(deck.getMedia())
        for media_info in media:
            self.AnkiBridge.storeMediaFile(
                media_info.get("fileName"), media_info.get("data"))

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
                        {"fileName": i.fileName, "data": base64.b64encode(i.data).decode("utf-8")})
        return formattedMedia

    def _buildNewDecksAsRequired(self, deck_names):
        new_deck_paths = []
        for deck_name in deck_names:
            full_deck_path = self._getFullDeckPath(deck_name)
            if full_deck_path not in self.AnkiBridge.deckNames() and full_deck_path not in new_deck_paths:
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
        builtNote = self.buildIndividualAnkiNotes([note])[0]
        self.AnkiBridge.addNote(builtNote)

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
