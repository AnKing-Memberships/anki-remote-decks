import os

# Configuraiton varibles
homePath = os.path.expanduser("~")
defaultOrgFile = "/orgNotes/quickOrgNotes.org"
quickNotesOrgPath = homePath + defaultOrgFile
quickNotesDirectory = homePath + "/orgNotes"
defaultDeck = "Remote Decks"
defaultDeckConnector = "::"
defaultAnkiConnectAddress = "http://127.0.0.1:8765/"
lazyLoadImages=False