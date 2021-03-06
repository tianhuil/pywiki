import argparse
import csv
import re
from collections import Counter
from functools import reduce
from io import StringIO
from itertools import islice
from typing import Iterator, Tuple

import mwparserfromhell
from lxml import etree
from smart_open import smart_open
from tqdm import tqdm

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


def parse_filter_page(pages: Iterator[str]) -> Iterator[dict]:
    """
    Parse page and ignore all administrative articles like

    - "User:SimonMayer"
    - "Talk:Wiki"
    - "User talk:Sikilai"
    - "Wikipedia:Image use policy"
    - "MediaWiki:Googlesearch"
    - "MediaWiki talk:Prefslogintext"
    - "Wikipedia talk:Copyrights"
    - "Template:Stub"

    Since there are so many types of articles, we choose to just ignore titles
    containing ":", accepting that we may occasionally over filter rather, rather
    than specifying all the administrative types.
    """
    for page in pages:
        tree = etree.parse(StringIO(page))
        title = tree.xpath("/page/title")[0].text

        if ":" in title:
            continue

        yield {
            "title": title,
            "id": tree.xpath("/page/id")[0].text,
            "timestamp": tree.xpath("/page/revision/timestamp")[0].text,
            "model": tree.xpath("/page/revision/model")[0].text,
            "format": tree.xpath("/page/revision/format")[0].text,
            "text": tree.xpath("/page/revision/text")[0].text,
        }


def admin_link(node):
    """
    Returns if a link to something like "[[Category:car]]" but not "[[car]]"
    """
    if isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
        return ":" in node.title
    return False


def heading(node):
    """
    Returns if this is a heading
    """
    return isinstance(node, mwparserfromhell.nodes.heading.Heading)


def parse_mw(iterator: Iterator[dict]) -> Iterator[str]:
    """
    parse markdownwiki format.  Remove links to

    - internal admin pages (e.g. "[[Category:X]]")
    - headings (e.g. "===References===")

    which generate vocabulary that throws off the count
    """
    for item in iterator:
        wikicode = mwparserfromhell.parse(item["text"])
        new_wikicode = mwparserfromhell.wikicode.Wikicode(
            [
                node
                for node in wikicode.ifilter(recursive=False)
                if (not admin_link(node)) and (not heading(node))
            ]
        )
        yield new_wikicode.strip_code()


def parse_text(iter: Iterator[str]) -> Iterator[str]:
    for item in iter:
        for word in RE_WORD.findall(item):
            yield word.lower()


RE_WORD = re.compile(r"[\w']+")


def aggregate_words(words: Iterator[str]) -> Tuple[Counter, int]:
    counter: Counter = Counter()
    count = 0
    for word in words:
        counter[word] += 1
        count += 1

    return counter, count


# from https://www.geeksforgeeks.org/function-composition-in-python/
def composite_function(*funcs):
    """
    compose
    """

    def compose(f, g):
        return lambda x: f(g(x))

    return reduce(compose, reversed([f for f in funcs if f]), lambda x: x)


def parse_args(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_file", help="input file")
    parser.add_argument("output_file", help="input file")
    parser.add_argument(
        "-l", "--limit", type=int, default=None, help="set limit on input arguements"
    )
    parser.add_argument(
        "-m", "--min", type=int, default=0, help="minimum count exported"
    )
    parser.add_argument("-s", "--silent", action="store_true", help="silence tqdm")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args("Parses wiki xml file")
    parse = composite_function(
        lambda x: islice(x, args.limit),
        parse_xml,
        parse_filter_page,
        tqdm if not args.silent else None,
        parse_mw,
        parse_text,
        aggregate_words,
    )
    with smart_open(args.input_file, encoding="utf-8") as input:
        with smart_open(args.output_file, "w", encoding="utf-8") as output:
            counter, total_count = parse(input)
            csv_writer = csv.writer(output)
            csv_writer.writerow(["word", "count", "fraction"])
            for word, count in counter.most_common():
                if count >= args.min:
                    csv_writer.writerow([word, count, 1.0 * count / total_count])
