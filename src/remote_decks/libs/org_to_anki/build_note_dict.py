from typing import Dict

from aqt import mw

from .ankiClasses.ParsedNote import ParsedNote


def build_note_dict(parsed_note: ParsedNote, root_deck=None) -> Dict:

    assert parsed_note.deckName
    if root_deck is not None:
        deckName = f"{root_deck}::{parsed_note.deckName}"
    else:
        deckName = parsed_note.deckName

    modelName = parsed_note.getParameter("Note type", "Basic")
    note = {"deckName": deckName, "modelName": modelName}

    note["tags"] = parsed_note.getTags()

    note["fields"] = dict()
    field_infos = mw.col.models.by_name(modelName)['flds']
    field_names = [field["name"] for field in field_infos]

    note["fields"][field_names[0]] = parsed_note.getQuestions()[0]
    answers = parsed_note.getAnswers()
    for field_name, answer in zip(field_names[1:], answers):
        note["fields"][field_name] = answer

    return note
