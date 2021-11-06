from ..ankiClasses.AnkiDeck import AnkiDeck
from .ParserUtils import getImageFromUrl
from .ParserUtils import convertLineToParameters
from .. import config

import os
import re
import hashlib

class DeckBuilderUtils:

    def __init__(self):

        self.lazyLoadImages = config.lazyLoadImages

    def parseAnswerLine(self, answerLine, filePath, currentQuestion):

        result = answerLine

        # Check if line needs to be parsed
        if re.search("\[image=[^]]+\]", answerLine):
            # Image metadata
            # TODO we are getting Spans in here and are creating nonsense characters

            # XXX there has to be a comment, or this fails
            line_parameters = convertLineToParameters(answerLine.split("#")[-1].strip())

            url_sections = re.findall("\[image=[^]]+\]", answerLine.strip())
            for url_section in url_sections:
                url = url_section.replace("[image=", "")[:-1]
                image_name = "downloaded_image_" + hashlib.md5(url_section.encode()).hexdigest()

                if config.lazyLoadImages == True:
                    currentQuestion.addLazyImage(image_name, url, getImageFromUrl)
                else:
                    imageData = getImageFromUrl(url)
                    currentQuestion.addImage(image_name, imageData)

                imageHtml = self.buildImageLine(image_name, {})
                result = re.sub("\[image=[^]]+\]", imageHtml, result, count=1)

            # Remove comment
            # XXX there has to be a comment, or this fails
            if len(line_parameters) > 0:
                result = result.rsplit("#", maxsplit=1)[0]

        return result
    
    def buildImageLine(self, imagePath, parameters={}):

        # Check if any specific line paramters
        if len(parameters) > 0:
            styles = ""
            for key in parameters.keys():
                styles += "{}:{};".format(key, parameters.get(key))
            return '<img src="{}" style="{}" />'.format(imagePath, styles)
        else:
            return '<img src="{}" />'.format(imagePath)

    def removeAsterisk(self, line): # (str)
        if line.strip()[0] == "*":
            line = line.strip().split(" ")[1:]
            line = " ".join(line)
            return line
        else:
            return line

    def countAsterisk(self, line): # (str)
        return line.split(' ')[0].count('*', 0, 10)

    def generateSublist(self, subItems): # ([str])

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

    def formatLine(self, line): # (str)

        formattedLine = line

        # Strip extra spaces for multiline
        if "\n" in formattedLine:
            cleanLine = ""
            for i in formattedLine.split("\n"):
                cleanLine += i.strip() + "\n"
            formattedLine = cleanLine.strip()

        return formattedLine
