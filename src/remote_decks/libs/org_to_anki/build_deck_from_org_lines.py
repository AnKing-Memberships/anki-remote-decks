from .org_parser import NoteFactoryUtils, ParserUtils
from .parse_classes.ParsedDeck import ParsedDeck
from .parse_classes.ParsedNote import ParsedNote


def build_deck_from_org_lines(lines, deckName):

    deck = ParsedDeck(deckName)
    groups = grouped_lines(lines)

    current_parameters = dict()
    for type, group_lines in groups:

        if type == "note":
            new_anki_note = parse(group_lines, current_parameters)
            deck.add_note(new_anki_note)

        elif type == "comment":
            for comment in group_lines:
                current_parameters.update(ParserUtils.convertLineToParameters(comment))

    return deck


def parse(lines, parameters) -> ParsedNote:

    utils = NoteFactoryUtils.NoteFactoryUtils()
    result = ParsedNote()

    # Add question
    question = lines[0]
    line = utils.remove_asterisks(question)
    line = utils.substitute_img_tags(line, result)
    result.addQuestion(line)

    # Add answers
    answers = lines[1:]
    for answer in answers:
        line = utils.remove_asterisks(answer)
        line = utils.substitute_img_tags(line, result)
        result.addAnswer(line)

    # Add parameters
    for key, val in parameters.items():
        result.setParameter(key, val)

    return result


def grouped_lines(lines):
    result = []
    cur_lines = lines[:]
    while cur_lines:
        line = cur_lines.pop(0)

        if line.startswith("* "):
            group_lines = [line]
            while cur_lines and (
                cur_lines[0].startswith("** ") or cur_lines[0].strip() == ""
            ):
                line = cur_lines.pop(0)
                group_lines.append(line)
            result.append(("note", group_lines))

        elif line.startswith("# "):
            group_lines = [line]
            while cur_lines and (
                cur_lines[0].startswith("# ") or cur_lines[0].strip() == ""
            ):
                line = cur_lines.pop(0)
                group_lines.append(line)
            result.append(("comment", group_lines))

    return result
