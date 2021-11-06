
from typing import Dict, List, Tuple

from anki.notes import Note
from aqt import mw

from .libs.org_to_anki.parse_classes import ParsedDeck
from .libs.org_to_anki.note_dict_from_parsed_note import note_dict_from_parsed_note


def deck_diff(remote_deck: ParsedDeck, local_notes: List[Note]):

    # the id is a tuple of the form: (first field content, modelName)
    note_by_id: Dict[Tuple[str, str], Note] = dict()
    for remote_note in local_notes:
        key = _get_key(remote_note)
        note_by_id[(key, remote_note["modelName"])] = remote_note

    def local_note_for_remote_note(remote_note):
        note_dict = note_dict_for_remote_note(remote_note)
        key = _get_key(note_dict)
        result = note_by_id.get((key, note_dict["modelName"]), None)
        return result

    def note_dict_for_remote_note(remote_note):
        result = note_dict_from_parsed_note(remote_note)
        return result

    new_notes = []
    udpated_notes = []
    removed_notes = []
    for remote_note in remote_deck.get_notes():
        local_note = local_note_for_remote_note(remote_note)

        if local_note is None:
            # new note
            new_notes.append((remote_note, -1))
        else:
            # updated note
            note_dict = note_dict_for_remote_note(remote_note)
            changed = False
            for fields in local_note.get("fields").keys():
                if not (local_note.get("fields").get(fields).get("value") == note_dict.get("fields").get(fields)):
                    changed = True
                    break
            if local_note["tags"] != note_dict["tags"]:
                changed = True

            if changed:
                udpated_notes.append((remote_note, local_note["noteId"]))

    remote_note_ids = set()
    for remote_note in remote_deck.get_notes():
        note_dict = note_dict_for_remote_note(remote_note)
        remote_note_ids.add((_get_key(note_dict), note_dict["modelName"]))

    for id_, local_note in note_by_id.items():
        if id_ not in remote_note_ids:
            noteId = local_note["noteId"]
            removed_notes.append((None, noteId))

    return {"new_notes": new_notes, "updated_notes": udpated_notes, "removed_notes": removed_notes}


def _get_key(note):
    # works for anki.notes.Note and for org_to_anki's AnkiNote
    key_field_name = mw.col.models.by_name(note["modelName"])[
        "flds"][0]["name"]
    temp = note["fields"][key_field_name]
    if isinstance(temp, str):
        return temp
    else:
        return temp["value"]
