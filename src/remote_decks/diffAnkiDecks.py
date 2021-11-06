
from typing import Dict, List, Tuple

from anki.notes import Note
from aqt import mw

from .libs.org_to_anki.ankiClasses import AnkiDeck
from .libs.org_to_anki.ankiConnectWrapper.AnkiNoteBuilder import \
    AnkiNoteBuilder


def diffAnkiDecks(remote_deck: AnkiDeck, local_notes: List[Note]):

    # the id is a tuple of the form: (first field content, modelName)
    note_by_id: Dict[Tuple[str, str], Note] = dict()
    for remote_note in local_notes:
        key = _get_key(remote_note)
        note_by_id[(key, remote_note["modelName"])] = remote_note

    def local_note_for_remote_note(remote_note):
        built_note = built_note_for_remote_note(remote_note)
        key = _get_key(built_note)
        result = note_by_id.get((key, built_note["modelName"]), None)
        return result

    def built_note_for_remote_note(remote_note):
        note_builder = AnkiNoteBuilder()
        result = note_builder.built_note(remote_note)
        return result

    new_notes = []
    udpated_notes = []
    removed_notes = []
    for remote_note in remote_deck.getQuestions():
        local_note = local_note_for_remote_note(remote_note)

        if local_note is None:
            # new note
            new_notes.append({"question": remote_note, "noteId": -1})
        else:
            # updated note
            built_note = built_note_for_remote_note(remote_note)
            changed = False
            for fields in local_note.get("fields").keys():
                if not (local_note.get("fields").get(fields).get("value") == built_note.get("fields").get(fields)):
                    changed = True
                    break
            if local_note["tags"] != built_note["tags"]:
                changed = True
            
            if changed:
                udpated_notes.append({"question": remote_note, "noteId": local_note["noteId"]})

    remote_note_ids = set()
    for remote_note in remote_deck.getQuestions():
        built_note = built_note_for_remote_note(remote_note)
        remote_note_ids.add((_get_key(built_note), built_note["modelName"]))

    for id_, local_note in note_by_id.items():
        if id_ not in remote_note_ids:
            noteId = local_note["noteId"]
            removed_notes.append({"question": local_note, "noteId": noteId})

    return {"newQuestions": new_notes, "questionsUpdated": udpated_notes, "removedQuestions": removed_notes}


def _get_key(note):
    # works for anki.notes.Note and for org_to_anki's AnkiNote
    key_field_name = mw.col.models.by_name(note["modelName"])[
        "flds"][0]["name"]
    temp = note["fields"][key_field_name]
    if isinstance(temp, str):
        return temp
    else:
        return temp["value"]
