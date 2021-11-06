
from .ankiClasses.AnkiDeck import AnkiDeck
from .ankiClasses.AnkiNoteFactory import AnkiNoteFactory


def build_new_deck(lines, deckName):

    deck = AnkiDeck(deckName)
    note_factory = AnkiNoteFactory(deckName)

    groups = grouped_lines(lines)

    section_comments = []
    for type, group_lines in groups:

        if type == "note":
            for comment in section_comments:
                note_factory.addCommentLine(comment)

            note_factory.addQuestionLine(group_lines[0])
            for field in group_lines[1:]:
                note_factory.addAnswerLine(field)

            newQuestion = note_factory.buildNote()
            deck.addQuestion(newQuestion)

        elif type == "comment":
            section_comments = []
            for line in group_lines:
                section_comments.append(line)

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
