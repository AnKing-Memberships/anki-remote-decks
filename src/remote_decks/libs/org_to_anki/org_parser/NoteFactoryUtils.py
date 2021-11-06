from .ParserUtils import getImageFromUrl
from .. import config

import re
import hashlib


class NoteFactoryUtils:

    def __init__(self):

        self.lazyLoadImages = config.lazyLoadImages

    def parseLine(self, line, note):
        result = line

        if re.search("\[image=[^]]+?\]", line):
            image_re = "\[image=(.+?), height=(.+?), width=(.+?)]"
            url_sections = re.findall(image_re, line)
            for url_section in url_sections:
                url, height, width = url_section
                image_name = "img_" + hashlib.md5(url.encode()).hexdigest()
                note.addLazyImage(image_name, url, getImageFromUrl)

                image_html = f'<img src="{image_name}" height={height} width={width} />'
                result = re.sub("\[image=[^]]+?\]",
                                image_html, result, count=1)

        return result

    def removeAsterisk(self, line):  # (str)
        if line.strip()[0] == "*":
            line = line.strip().split(" ")[1:]
            line = " ".join(line)
            return line
        else:
            return line

    def countAsterisk(self, line):  # (str)
        return line.split(' ')[0].count('*', 0, 10)

    def generateSublist(self, subItems):  # ([str])

        formatedList = []

        indentationLevel = self.countAsterisk(subItems[0])
        for item in subItems:
            if self.countAsterisk(item) == indentationLevel:
                formatedList.append(item)
            elif self.countAsterisk(item) > indentationLevel and isinstance(formatedList[-1], list):
                formatedList[-1].append(item)
            else:
                formatedList.append([item])

        cleaned = []
        for i in formatedList:
            if isinstance(i, list):
                cleaned.append(self.generateSublist(i))
            else:
                cleaned.append(self.removeAsterisk(i))

        return cleaned

    def formatLine(self, line):  # (str)

        formattedLine = line

        # Strip extra spaces for multiline
        if "\n" in formattedLine:
            cleanLine = ""
            for i in formattedLine.split("\n"):
                cleanLine += i.strip() + "\n"
            formattedLine = cleanLine.strip()

        return formattedLine
