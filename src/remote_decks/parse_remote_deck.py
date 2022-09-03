import re

import bs4
import requests
from bs4 import BeautifulSoup

from .libs.org_to_anki import config
from .libs.org_to_anki.build_deck_from_org_lines import build_deck_from_org_lines


# Should get the remote deck and return an Anki Deck
def getRemoteDeck(url):

    # Get remote page
    # TODO Validate url before getting data
    if url.startswith("https://docs.google.com/") and not url.endswith("pub"):
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
    if documentString in url:
        return "html"
    elif csvString in url:
        return "csv"
    else:
        return None


def _parseHtmlPageToAnkiDeck(data):

    orgData = _generateOrgListFromHtmlPage(data)
    deckName = orgData["deckName"]
    lines = orgData["data"]

    # Ensure images are lazy loaded to reduce load
    config.lazyLoadImages = True
    deck = build_deck_from_org_lines(lines, deckName)

    return deck


def _extract_css_styles(style_item: bs4.element.Tag):

    # Google docs uses c1, c2, ... classes for styling
    css_section_re = "\.c\d+\{[\w\W]+?}"
    html_str = style_item.decode_contents()
    css_sections = re.findall(css_section_re, html_str)

    result = {}

    # for each c section extract critical data
    data_re = ":[^;^}\s]+[;}]"
    section_start_re = "[;{]"
    for section in css_sections:
        name = re.findall("c[\d]+", section)[0]
        color = re.findall("{}{}{}".format(section_start_re, "color", data_re), section)
        font_style = re.findall(
            "{}{}{}".format(section_start_re, "font-style", data_re), section
        )
        font_weight = re.findall(
            "{}{}{}".format(section_start_re, "font-weight", data_re),
            section,
        )
        text_decoration = re.findall(
            "{}{}{}".format(section_start_re, "text-decoration", data_re),
            section,
        )
        vertical_align = re.findall(
            "{}{}{}".format(section_start_re, "vertical-align", data_re),
            section,
        )

        # Ignore default values
        if len(color) > 0 and "color:#000000" in color[-1]:
            color = []
        if len(font_weight) > 0 and "font-weight:400" in font_weight[-1]:
            font_weight = []
        if len(font_style) > 0 and "font-style:normal" in font_style[-1]:
            font_style = []
        if len(text_decoration) > 0 and "text-decoration:none" in text_decoration[-1]:
            text_decoration = []
        if len(vertical_align) > 0 and "vertical-align:baseline" in vertical_align[-1]:
            vertical_align = []

        style_rules = [color, font_style, font_weight, text_decoration, vertical_align]
        style_values = []
        for style_rule in style_rules:
            if len(style_rule) > 0:
                cleaned_style = style_rule[-1][1:-1]
                style_values.append(cleaned_style)

        result[name] = style_values

    return result


def _generateOrgListFromHtmlPage(cell_content):

    soup = BeautifulSoup(cell_content, "html.parser")
    title = soup.find("div", {"id": "title"})
    deckName = title.text
    contents = soup.find_all(["table", "p"])

    css_styles = {}  # dict from class name to style rules
    for styles_item in soup.find_all("style"):
        css_styles.update(_extract_css_styles(styles_item))

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
        elif item.name == "p":
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
            for row in item.find_all("tr"):
                cell_content = row.find("td")
                _apply_styles(cell_content, css_styles)

                images = cell_content.find_all("img")
                for img in images:
                    styles = img["style"]
                    width = (
                        m.group(1) if (m := re.search("width: (.+?);", styles)) else ""
                    )
                    height = (
                        m.group(1) if (m := re.search("height: (.+?);", styles)) else ""
                    )
                    image_text = f"[image={img['src']}, height={height}, width={width}]"
                    img.parent.insert_after(image_text)
                    _clean_up(img)

                if (
                    not (chs := cell_content.contents)
                    or (len(chs) == 1 and chs[0].name == "p" and not chs[0].contents)
                    or (all(isinstance(x, str) and x.strip() == "" for x in chs))
                ):
                    # append empty row if the table row is empty apart from whitespace
                    rows.append("")
                else:
                    cell_html = cell_content.decode_contents()
                    cell_html = substitute_cloze_aliases(cell_html)
                    rows.append(cell_html)

            if all(row.strip() == "" for row in rows):
                # ignore empty tables
                continue

            orgFormattedFile.append(f"* {rows[0]}")
            for x in rows[1:]:
                orgFormattedFile.append(f"** {x}")

    return {"deckName": deckName, "data": orgFormattedFile}


def substitute_cloze_aliases(html):
    result = html
    cloze_idx = 1
    alias_re = "\$(\d*)\$(.+?)\$\$"
    while m := re.search(alias_re, result):
        number, text = m.groups()
        cur_idx = number if number else cloze_idx
        result = re.sub(
            alias_re, f"{{{{c{cur_idx}::{text.strip()}}}}}", result, count=1
        )
        cloze_idx += 1
    return result


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
        if "#multilinecommentstart" == line.replace(" ", "").lower():
            return True
    return False


def _endOfMultiLineComment(item):

    # Get span text
    if item.name == "p":
        line = ""
        sections = item.find_all("span")
        for span in sections:
            line += span.text
        if "#multilinecommentend" == line.replace(" ", "").lower():
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
        _apply_styles(child, cssStyles, depth=depth + 1)

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
