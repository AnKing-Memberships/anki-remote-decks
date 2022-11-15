
from anki.models import ModelManager
from anki.notes import Note


def add_compat_aliases():
    add_compat_alias(ModelManager, "by_name", "byName")
    add_compat_alias(Note, "note_type", "model")


def add_compat_alias(namespace, new_name, old_name):
    if new_name not in dir(namespace):
        setattr(namespace, new_name, getattr(namespace, old_name))
        return True

    return False
