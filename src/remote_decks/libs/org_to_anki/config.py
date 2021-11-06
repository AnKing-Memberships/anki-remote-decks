import os

# Configuraiton varibles
homePath = os.path.expanduser("~")
defaultOrgFile = "/orgNotes/quickOrgNotes.org"
quickNotesOrgPath = homePath + defaultOrgFile
quickNotesDirectory = homePath + "/orgNotes"
rootDeck = "Remote decks" # XXX this should be set elsewhere so this has no effect, but it currently has
defaultDeckConnector = "::"
defaultAnkiConnectAddress = "http://127.0.0.1:8765/"
lazyLoadImages=False