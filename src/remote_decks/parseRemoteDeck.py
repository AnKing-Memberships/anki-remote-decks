import re

import requests
from bs4 import BeautifulSoup

from .libs.org_to_anki import config
from .libs.org_to_anki.org_parser.parseData import buildNamedDeck


# Should get the remote deck and return an Anki Deck
def getRemoteDeck(url):

    # Get remote page
    # TODO Validate url before getting data
    if url.startswith('https://docs.google.com/') and not url.endswith('pub'):
        raise Exception("Use the Publish link, not the Sharing link")
    pageType = _determinePageType(url)
    deck = None
    if pageType == "html":
        data = _download(url)
        deck = _parseHtmlPageToAnkiDeck(data)

    elif pageType == "csv":
        pass
    else:
        raise Exception("url is not a Google doc or csv file")

    return deck


def _determinePageType(url):

    # TODO use url to determine page types
    csvString = "/spreadsheets/"
    documentString = "/document/"
    if (documentString in url):
        return "html"
    elif (csvString in url):
        return "csv"
    else:
        return None


def _parseHtmlPageToAnkiDeck(data):

    orgData = _generateOrgListFromHtmlPage(data)
    deckName = orgData["deckName"]
    data = orgData["data"]

    # TODO update org_to_anki to have function for this
    # Ensure images are lazy loaded to reduce load
    config.lazyLoadImages = True
    deck = buildNamedDeck(data, deckName)

    return deck


def _getCssStyles(cssData):

    # Google docs used the following class for lists $c1
    cSectionRegexPattern = "\.c\d{1,2}\{[^\}]+}"
    cssSections = re.findall(cSectionRegexPattern, cssData.text)

    cssStyles = {}
    # for each c section extract critical data
    regexValuePattern = ":[^;^}\s]+[;}]"
    startSectionRegex = "[;{]"
    for section in cssSections:
        name = re.findall("c[\d]+", section)[0]
        color = re.findall("{}{}{}".format(
            startSectionRegex, "color", regexValuePattern), section)
        fontStyle = re.findall("{}{}{}".format(
            startSectionRegex, "font-style", regexValuePattern), section)
        fontWeight = re.findall("{}{}{}".format(
            startSectionRegex, "font-weight", regexValuePattern), section)
        textDecoration = re.findall("{}{}{}".format(
            startSectionRegex, "text-decoration", regexValuePattern), section)
        verticalAlign = re.findall("{}{}{}".format(
            startSectionRegex, "vertical-align", regexValuePattern), section)

        # Ignore default values
        if (len(color) > 0 and "color:#000000" in color[0]):
            color = []
        if (len(fontWeight) > 0 and "font-weight:400" in fontWeight[0]):
            fontWeight = []
        if (len(fontStyle) > 0 and "font-style:normal" in fontStyle[0]):
            fontStyle = []
        if (len(textDecoration) > 0 and "text-decoration:none" in textDecoration[0]):
            textDecoration = []
        if (len(verticalAlign) > 0 and "vertical-align:baseline" in verticalAlign[0]):
            verticalAlign = []

        d = [color, fontStyle, fontWeight, textDecoration, verticalAlign]

        styleValues = []
        for i in d:
            if len(i) > 0:
                cleanedStyle = i[0][1:-1]
                styleValues.append(cleanedStyle)
        cssStyles[name] = styleValues

    return cssStyles


def _generateOrgListFromHtmlPage(cell_content):

    soup = BeautifulSoup(cell_content, 'html.parser')
    title = soup.find("div", {"id": "title"})
    deckName = title.text
    contents = soup.find_all(["table", "p"])

    # Try and get CSS XXX
    # XXX code is weird
    cssData = soup.find_all("style")
    cssStyles = {}
    for css in cssData:
        styleSection = _getCssStyles(css)
        cssStyles.update(styleSection)

    multiCommentSection = False
    orgFormattedFile = []
    for item in contents:
        # Handle multiLine comment section
        if _startOfMultiLineComment(item):
            multiCommentSection = True
            continue
        elif multiCommentSection and _endOfMultiLineComment(item):
            multiCommentSection = False
            continue
        elif multiCommentSection:
            continue

        # Handle normal line
        if item.name == "p":
            # Get span text
            line = ""
            textSpans = item.find_all("span")
            for span in textSpans:
                line += span.text

            # Get link text
            linkText = ""
            allLinks = item.find_all("a")
            for link in allLinks:
                text = link.contents
                for t in text:
                    linkText += t

            # Ignore line if span and link text are the same
            if len(line) > 0 and linkText != line:
                orgFormattedFile.append(line)

        elif item.name == "table":
            rows = []
            imageConfig = ""
            for row in item.find_all('tr'):
                cell_content = row.find('td')
                _apply_styles(cell_content, cssStyles)

                images = cell_content.find_all("img")
                images_string = ""
                for img in images:
                    styles = img["style"]
                    searchRegex = "{}:\s[^;]*;"
                    height = re.findall(searchRegex.format("height"), styles)[0].split(":")[1].replace(";", "").strip()
                    width = re.findall(searchRegex.format("width"), styles)[0].split(":")[1].replace(";", "").strip()
                    image_text = f"[image={img['src']}]"
                    images_string += image_text
                    _clean_up(img)

                cell_html = cell_content.decode_contents()

                if images:
                    images_string += f" # height={height}, width={width}"
                    cell_html += images_string
                    if len(imageConfig) > 0:
                        cell_html += imageConfig

                rows.append(cell_html)

            orgFormattedFile.append(f"* {rows[0]}")
            for x in rows[1:]:
                orgFormattedFile.append(f"** {x}")

        else:
            print(f"Unknown line type: {item.name}")

    return {"deckName": deckName, "data": orgFormattedFile}

def _clean_up(item):
    parent = item.parent
    item.decompose()
    if not parent.contents:
        _clean_up(parent)

### Special cases ###


def _startOfMultiLineComment(item):

    # Get span text
    if item.name == "p":
        line = ""
        sections = item.find_all("span")
        for span in sections:
            line += span.text
        if ("#multilinecommentstart" == line.replace(" ", "").lower()):
            return True
    return False


def _endOfMultiLineComment(item):

    # Get span text
    if item.name == "p":
        line = ""
        sections = item.find_all("span")
        for span in sections:
            line += span.text
        if ("#multilinecommentend" == line.replace(" ", "").lower()):
            return True
    return False


def _apply_styles(item, cssStyles, depth=0):
    if not hasattr(item, "attrs"):
        return

    classes = item.attrs.get("class", None)
    if classes is None:
        return

    for class_ in classes:
        for style in cssStyles.get(class_, []):
            item["style"] = item.get("style", "") + style + "; "
    item.attrs.pop("class", None)

    for child in item.children:
        _apply_styles(child, cssStyles, depth=depth+1)

    # text in tables gets wrapped into p tags by default which should be removed
    if depth == 1 and item.name == "p" and len(list(item.children)) == 1:
        item.replace_with(list(item.children)[0])

    if item.name == "span" and len(item.attrs) == 0:
        item.unwrap()

    return item


def _download(url):

    response = requests.get(url)
    if response.status_code == 200:
        data = response.content
    else:
        raise Exception("Failed to get url: {}".format(response.status_code))

    data = data.decode("utf-8")
    data = data.replace("\xa0", " ")
    return data
