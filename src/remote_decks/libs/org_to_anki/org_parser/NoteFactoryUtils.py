import hashlib
import re

from .. import config
from .ParserUtils import getImageFromUrl


class NoteFactoryUtils:
    def __init__(self):

        self.lazyLoadImages = config.lazyLoadImages

    def substitute_img_tags(self, line, note):
        result = line

        if re.search("\[image=[^]]+?\]", line):
            image_re = "\[image=(.+?), height=(.+?), width=(.+?)]"
            url_sections = re.findall(image_re, line)
            for url_section in url_sections:
                url, height, width = url_section
                image_name = f"img_{hashlib.md5(url.encode()).hexdigest()}"
                note.addLazyImage(image_name, url, getImageFromUrl)

                image_html = f'<img src="{image_name}" height={height} width={width} />'
                result = re.sub("\[image=[^]]+?\]", image_html, result, count=1)

        return result

    def remove_asterisks(self, line):  # (str)
        if line.strip().startswith("*"):
            line = line.strip().split(" ")[1:]
            line = " ".join(line)
            return line
        else:
            return line
