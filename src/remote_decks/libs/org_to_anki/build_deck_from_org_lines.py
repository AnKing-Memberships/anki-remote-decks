
from .parse_classes.ParsedDeck import ParsedDeck
from .parse_classes.ParsedNoteFactory import ParsedNoteFactory


def build_deck_from_org_lines(lines, deckName):

    deck = ParsedDeck(deckName)
    note_factory = ParsedNoteFactory(deckName)

    groups = grouped_lines(lines)

    section_comments = []
    for type, group_lines in groups:

        if type == "note":
            for comment in section_comments:
                note_factory.addCommentLine(comment)

            note_factory.addQuestionLine(group_lines[0])
            for field in group_lines[1:]:
                note_factory.addAnswerLine(field)

            new_anki_note = note_factory.parse()
            deck.add_note(new_anki_note)

        elif type == "comment":
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
