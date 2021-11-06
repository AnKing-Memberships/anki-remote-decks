
from .ankiClasses.AnkiDeck import AnkiDeck
from .ankiClasses.AnkiQuestionFactory import AnkiQuestionFactory
from .org_parser import ParserUtils


def build_new_deck(lines, deckName):

    deck = AnkiDeck(deckName)

    questionFactory = AnkiQuestionFactory(deckName)

    groups = grouped_lines(lines)

    sectionParameters = {}
    for type, group_lines in groups:

        if type == "note":
            for key, value in sectionParameters.items():
                questionFactory.addCommentLine(f"# {key} : {value}")

            questionFactory.addQuestionLine(group_lines[0])
            for field in group_lines[1:]:
                questionFactory.addAnswerLine(field, sectionParameters)

            newQuestion = questionFactory.buildQuestion()
            deck.addQuestion(newQuestion)

        elif type == "comment":
            questionFactory.currentComments = []
            questionFactory.parameters = {}

            for line in group_lines:
                questionFactory.addCommentLine(line)
                parameters = ParserUtils.convertLineToParameters(line)
                for key in parameters.keys():
                    sectionParameters[key] = parameters.get(key)

    return deck


def grouped_lines(lines):
    result = []
    cur_lines = lines[:]
    while cur_lines:
        line = cur_lines.pop(0)

        if line.startswith("* "):
            group_lines = [line]
            while cur_lines and (cur_lines[0].startswith("** ") or cur_lines[0].strip() == ""):
                line = cur_lines.pop(0)
                group_lines.append(line)
            result.append(("note", group_lines))

        elif line.startswith("# "):
            group_lines = [line]
            while cur_lines and (cur_lines[0].startswith("# ") or cur_lines[0].strip() == ""):
                line = cur_lines.pop(0)
                group_lines.append(line)
            result.append(("comment", group_lines))

    return result
