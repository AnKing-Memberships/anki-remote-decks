# Google Doc Decks

[![Build Status](https://travis-ci.org/c-okelly/anki-remote-decks.svg?branch=master)](https://travis-ci.org/c-okelly/anki-remote-deck)

This anki add-on allows users to create Anki decks in Google Docs that can then be synced with Anki. The remote deck acts as the reference point or the source of truth. When a user syncs, cards are added / updated / deleted in the local deck. When cards are updated in the Google Doc (excluding the primary field), their history is preserved.

Official Add-on => [Google Doc Anki Decks](https://ankiweb.net/shared/info/911568091)

# Overview and Instructions

Use the link below to find instructions and examples

https://docs.google.com/document/d/17oB8IrIMTSwM99NaOWQG-RDK56kt8Haq2b84smW8h00/edit

# How does the add-on manage changes with note history?

* New notes are added without any history
* Notes removed from the Google doc are removed from the local deck
* If the answer section changes, the note is updated and history is preserved
* If the question line (primary field) changes, the old note is deleted and a new note is added.
  * History is lost for the note

# Formatting support

Currently, the following formatting is supported:

* Bold
* Underlined
* Italics
* Colors

# Using the Table of contents to sort your file

Users can now use a table of contents to index large files.

This allows users to create content at the top of the file and then create headings throughout. These will be ignored when generating questions

# Manage image size

Images can be sized by changing their size within the Google doc itself. The height and width in PX of the image are added to the Anki card.



# Contributing

The repo is not really set up currently for contributing. 

In order to package the repository, run the following scripts. This will generate a zip with the required files for an Anki Add-on

```
./installOrgToAnki.sh
./package.sh
```

# Issues

If you have an issue please file a GitHub issue! Thanks

# Future development

Future development will be tracked under issues as feature requests

# Contributors

Github user fneurohr22

# Change log

2024/05/04 - Released the add-on publicly

2020/04/-7 - Release of Version V1.5.2 => Fix delete issues

2020/01/26 - Release of Version V1.5.1 => Bugfix

2020/01/26 - Release of Version V1.5.0 => Check for default models and fix image metadata bug

2020/01/26 - Release of Version V1.4.1 => Support table of contents

2020/01/26 - Release of Version V1.4.0 => Improved Sync and add speed. Debug mode added

2020/01/25 - Release of Version V1.3.1 => Unicode bugfix

2019/11/09 - Release of Version V1.3.0 => Warning and image bugfix

2019/10/21 – Release of Version V1.2.2 => Brackets and formatting bugs

2019/09/30 – Release of Version V1.2.1 => Image bugfixes

2019/09/25 – Release of Version V1.2.0 => Unicode and formatting bugfixes

2019/09/08 – Release of Version V1.2.0 => Formatting for color, bold, italics and underline is now also parsed

2019/08/30 – Release of Version V1.1.1 => Bugfix the resulted in double images

2019/08/29 – Release of Version V1.1.1 => Bugfix in org_to_anki

2019/08/28 – Release of Version V1.1.0 => Bugfix in org_to_anki

2019/08/28 – Release of Version V1.0.1 => Improve error handling

2019/08/28 – Release of Version V1.0.0 => Support for Cloze and image

2019/06/2 – Release of Alpha version V0.1.0

2019/06/2 – Release of Beta version V0.0.1 
