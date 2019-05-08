import requests
import codecs
from bs4 import BeautifulSoup
import re

# Should get the remote deck and return an Anki Deck
def getRemoteDeck(url):

    # Get remote page
    # TODO Validate url before getting data
    pageType = _determinePageType(url)
    if pageType == "html":
        data = _download(url)
        orgPage = _parseHtmlPageToOrgFile(data)

    elif pageType == "csv":
        pass
    else:
        raise Exception("url is not a Google doc or csv file")
        
    return deck

def _determinePageType(url):

    # TODO use url to determine page types
    if (True):
        return "html"
    elif (False):
        return "csv"
    else:
        return None


def _parseHtmlPageToOrgFile(data):

    orglist = _generateOrgListFromHtmlPage(data)

def _generateOrgListFromHtmlPage(data):

    orgStar = "*"
    imageTemplate = "[{}]"
    soup = BeautifulSoup(data, 'html.parser')
    contents = soup.find("div", {"id":"contents"})

    orgFormattedFile = []
    for item in contents:
        print(item)
        if item.name == "p":
            # print("p")
            lineText = item.text
            if len(lineText) > 0:
                orgFormattedFile.append(lineText)

            # Check if line contains an image
            # print(item.find_all("img"))
            images = item.find_all("img")
            if len(images) == 1:
                # print("found an image")
                imageText = imageTemplate.format(images[0]["src"])
                orgFormattedFile.append(imageText)

            # TODO support multiple images after MVP and test
            elif len(images) > 1:
                raise Exception("Only one image per a line")

        elif item.name == "ul":
            print("ul")
            listItems = item.find_all("li")

            # Item class is in the format of "lst-kix_f64mhuyvzb86-1" with last numbers as the level
            classes = item["class"] #.split("-")[-1])
            regexSearch = "^[\w]{3}-[\w]{3,}-[\d]{1,}"
            indentation = -1
            for i in classes:
                if re.match(regexSearch, i) != None:
                    indentation = int(i.split("-")[-1])
            
            if (indentation == -1):
                raise Exception("Could not find the correct indentation")

            if len(listItems) == 1:
                itemText = listItems[0].text
            elif len(listItems) > 1:
                raise Exception("There should only be one list item")
            
            indentation += 1
            orgStars = (orgStar * indentation)
            formattedListItem = "{} {}".format(orgStars, itemText)

            orgFormattedFile.append(formattedListItem)
        else:
            print("Unknown line type: {}".format(item.name))
        
        # print(x.name)
        print()

    

    return orgFormattedFile

def _download(url):

    response = requests.get(url)
    if response.status_code == 200:
        data = response.content
    else:
        raise Exception("Failed to get url: {}".format(response.status_code))

    return data

if __name__ == "__main__":
    pass
