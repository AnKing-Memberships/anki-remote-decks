from .ParsedNoteMedia import ParsedNoteMedia


class ParsedNote:
    def __init__(self):
        self.deckName = None
        self.question = []
        self._answers = []
        self._parameters = {}
        self._media = []

    def setDeckName(self, deckName):
        self.deckName = deckName

    def getDeckName(self):
        return self.deckName

    def addQuestion(self, question):
        self.question.append(question)

    def getQuestions(self):
        return self.question

    def addImage(self, fileName, fileData):
        self._media.append(ParsedNoteMedia("image", fileName, fileData))

    def addLazyImage(self, fileName, url, imageFunc):
        self._media.append(
            ParsedNoteMedia(
                "image", fileName, data=None, imageUrl=url, imageFunction=imageFunc
            )
        )

    def hasMedia(self):
        return len(self._media) > 0

    def getMedia(self):
        return self._media

    # Getters and setters #
    def addAnswer(self, answer):  # (str)
        self._answers.append(answer)

    def getAnswers(self):
        return self._answers

    def setParameter(self, key, value):  # (str, str)
        self._parameters[key] = value

    def getParameter(self, key, default=None):
        return self._parameters.get(key, default)

    def getTags(self):
        return self._parameters.get("Tag", "").split(",")
