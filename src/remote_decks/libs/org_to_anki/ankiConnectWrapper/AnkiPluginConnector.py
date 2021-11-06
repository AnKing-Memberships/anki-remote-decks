import base64

from .. import config
from ..build_note_dict import build_note_dict
from .AnkiBridge import AnkiBridge
from .AnkiNoteBuilder import AnkiNoteBuilder

try:
    import aqt

    from ..noteModels.models import NoteModels
except:
    pass


class AnkiPluginConnector:

    def __init__(self, defaultDeck=config.defaultDeck):
        self.AnkiBridge = AnkiBridge()
        self.root_deck = defaultDeck
        self.AnkiNoteBuilder = AnkiNoteBuilder(self.root_deck)

    def create_new_deck(self, deck):

        self._buildNewDecksAsRequired(deck.getDeckNames())

        # Build new notes
        notes = self.buildIndividualAnkiNotes(deck.getQuestions())
        media = self.prepareMedia(deck.getMedia())

        # Add notes
        for note in notes:
            self.AnkiBridge.addNote(note)

        # Add media
        for media_info in media:
            self.AnkiBridge.storeMediaFile(media_info.get("fileName"), media_info.get("data"))

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

    def buildAnkiNotes(self, ankiQuestions):  # [AnkiQuestion]

        notes = []
        for i in ankiQuestions:
            notes.append(self.AnkiNoteBuilder.built_note(i))

        finalNotes = {}
        finalNotes["notes"] = notes
        return finalNotes

    def buildIndividualAnkiNotes(self, anki_notes):
        allNotes = []
        for note in anki_notes:
            allNotes.append(build_note_dict(note, self.root_deck))

        return allNotes

    ### These methods are still in beta and are subject to change ###

    # Get deck Notes
    def getDeckNotes(self, deckName):
        # TODO => revisit return type
        return self.AnkiBridge.getDeckNotes(deckName)

    # Add new notes
    def addNote(self, note):
        builtNote = self.buildIndividualAnkiNotes([note])[0]
        self.AnkiBridge.addNote(builtNote)

    # Delete notes
    def deleteNotes(self, noteIds):
        self.AnkiBridge.deleteNotes(noteIds)

    # Update Note fields
    def updateNoteFields(self, note):

        # TODO ensure note is logically correct
        self.AnkiBridge.updateNoteFields(note)

    def getConfig(self):
        return aqt.mw.addonManager.getConfig(__name__)

    def writeConfig(self, config):
        aqt.mw.addonManager.writeConfig(__name__, config)

    # Check for a file
    def checkForMediaFile(self, filename):
        return self.AnkiBridge.checkForMediaFile(filename)

    def startEditing(self):
        self.AnkiBridge.startEditing()

    def stopEditing(self):
        self.AnkiBridge.stopEditing()

    # Check for note models and add them if they do not exists

    def checkForDefaultModelsInEnglish(self):
        # Be default we expect the following english named models
        # Basic, Basic (and reversed card) and Cloze

        models = self.AnkiBridge.modelNames()
        localModels = NoteModels()

        # Create Basic
        if "Basic" not in models:
            model = localModels.getBasicModel()

            self.AnkiBridge.createModel(model.get("name"), model.get(
                "inOrderFields"), model.get("cardTemplates"), model.get("css"))

        # Create Basic and reversed
        if "Basic (and reversed card)" not in models:
            model = localModels.getRevseredModel()

            self.AnkiBridge.createModel(model.get("name"), model.get(
                "inOrderFields"), model.get("cardTemplates"), model.get("css"))

        # Create Close
        if "Cloze" not in models:
            model = localModels.getClozeModel()

            self.AnkiBridge.createModel(model.get("name"), model.get(
                "inOrderFields"), model.get("cardTemplates"), model.get("css"))
