import argparse
import re
from io import StringIO
from itertools import islice
from typing import Iterator

from lxml import etree
from smart_open import smart_open

RE_START = re.compile("\s+<page>$")
RE_END = re.compile("\s+</page>$")


def parse_xml(lines: Iterator[str]) -> Iterator[str]:
    memory = ""
    for line in lines:
        if RE_START.match(line):
            memory = ""
        memory += line
        if RE_END.match(line):
            yield memory


def parse_page(pages: Iterator[str]) -> Iterator[dict]:
    for page in pages:
        tree = etree.parse(StringIO(page))
        yield {
            "title": tree.xpath("/page/title")[0].text,
            "id": tree.xpath("/page/id")[0].text,
            "timestamp": tree.xpath("/page/revision/timestamp")[0].text,
            "model": tree.xpath("/page/revision/model")[0].text,
            "format": tree.xpath("/page/revision/format")[0].text,
            "text": tree.xpath("/page/revision/text")[0].text,
        }


def parse_args(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_file", help="input file")
    parser.add_argument("output_file", help="input file")
    parser.add_argument(
        "-l", "--limit", type=int, default=None, help="set limit on input arguements"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args("Parses wiki xml file")
    with smart_open(args.input_file, encoding="utf-8") as fh:
        for blob in parse_page(parse_xml(islice(fh, args.limit))):
            print(blob)
            print("#" * 40)
