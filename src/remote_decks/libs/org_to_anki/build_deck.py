
from .ankiClasses.AnkiDeck import AnkiDeck
from .ankiClasses.AnkiQuestionFactory import AnkiQuestionFactory


def build_new_deck(lines, deckName):

    deck = AnkiDeck(deckName)

    questionFactory = AnkiQuestionFactory(deckName)

    groups = grouped_lines(lines)

    sectionComments = []
    for type, group_lines in groups:

        if type == "note":
            for comment in sectionComments:
                questionFactory.addCommentLine(comment)

            questionFactory.addQuestionLine(group_lines[0])
            for field in group_lines[1:]:
                questionFactory.addAnswerLine(field)

            newQuestion = questionFactory.buildQuestion()
            deck.addQuestion(newQuestion)

        elif type == "comment":
            sectionComments = []
            for line in group_lines:
                sectionComments.append(line)

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
