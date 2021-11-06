from .AnkiNote import AnkiNote
from ..org_parser import NoteFactoryUtils
from ..org_parser import ParserUtils


class AnkiNoteFactory:

    utils = NoteFactoryUtils.NoteFactoryUtils()

    def __init__(self, currentDeck, indentor="*"):
        self.currentDeck = currentDeck
        self.indentor = indentor
        self.currentQuestions = []
        self.currentAnswers = []
        self.currentComments = []
        self.parameters = {}

    # Clear the current data
    def clearData(self):
        self.currentQuestions = []
        self.currentAnswers = []
        self.currentComments = []
        self.parameters = {}

    def hasData(self):
        return len(self.currentQuestions) == 0 or len(self.currentAnswers) == 0 and len(self.currentComments) == 0

    def addAnswerLine(self, line):
        metadata = self.parameters
        self.currentAnswers.append({"line": line, "metadata": metadata})

    def addQuestionLine(self, question):
        self.currentQuestions.append(question)

    def addCommentLine(self, comment):
        self.currentComments.append(comment)
        parameters = ParserUtils.convertLineToParameters(comment)
        for key in parameters.keys():
            self.parameters[key] = parameters.get(key)

    # Utility
    def isValidQuestion(self):
        # Check for one of following three conditions
        # 1. Has answers
        # 2. Has a code section
        # 3. Has card type cloze
        return len(self.currentAnswers) > 0 or len(self.codeSection) > 0 or self.parameters.get("type") == "Cloze" or self.parameters.get("type") == "Cloze"

    def buildNote(self):

        new_note = AnkiNote()

        # Add Question (it's always just one question XXX)
        for line in self.currentQuestions:
            line = self.utils.removeAsterisk(line)
            line = self.utils.formatLine(line)
            line = self.utils.parseLine(line, new_note)
            new_note.addQuestion(line)

        # Add answers
        for dataLine in self.currentAnswers:
            line = dataLine.get("line")
            fieldName = dataLine.get("metadata").get("fieldName", None)
            line = self.utils.removeAsterisk(line)
            line = self.utils.parseLine(line, new_note)
            new_note.addAnswer(line, fieldName)

        # Add comments
        for comment in self.currentComments:
            new_note.addComment(comment)
            parameters = ParserUtils.convertLineToParameters(comment)
            for key in parameters.keys():
                new_note.addParameter(key, parameters.get(key))

        # Clear data and return
        self.clearData()

        return new_note
