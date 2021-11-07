from typing import Dict

from aqt import mw

from .parse_classes.ParsedNote import ParsedNote


class NoteTypeDoesntExistException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def note_dict_from_parsed_note(parsed_note: ParsedNote, root_deck=None) -> Dict:

    assert parsed_note.deckName
    if root_deck is not None:
        deckName = f"{root_deck}::{parsed_note.deckName}"
    else:
        deckName = parsed_note.deckName

    model_name = parsed_note.getParameter("Note type", "Basic")
    note = {"deckName": deckName, "modelName": model_name}

    note["tags"] = parsed_note.getTags()

    note["fields"] = dict()
    model = mw.col.models.by_name(model_name)
    if not model:
        raise NoteTypeDoesntExistException(f"There is no \"{model_name}\" note type.")

    field_names = [field["name"] for field in model["flds"]]

    note["fields"][field_names[0]] = parsed_note.getQuestions()[0]
    answers = parsed_note.getAnswers()
    for field_name, answer in zip(field_names[1:], answers):
        note["fields"][field_name] = answer

    return note
