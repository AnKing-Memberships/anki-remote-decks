from typing import Dict

from aqt import mw

from . import config


def built_note(anki_note) -> Dict:

    assert anki_note.deckName
    deckName = f"{config.defaultDeck}::{anki_note.deckName}"

    modelName = anki_note.getParameter("Note type", "Basic")
    note = {"deckName": deckName, "modelName": modelName}

    note["tags"] = anki_note.getTags()

    note["fields"] = dict()
    field_infos = mw.col.models.by_name(modelName)['flds']
    field_names = [field["name"] for field in field_infos]

    note["fields"][field_names[0]] = anki_note.getQuestions()[0]
    answers = anki_note.getAnswers()
    for field_name, answer in zip(field_names[1:], answers):
        note["fields"][field_name] = answer

    return note
