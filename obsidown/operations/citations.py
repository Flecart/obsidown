"""Convert a citation format to a link citation format."""

from obsidown.operations.base import MdFile, MdOperations
import bibtexparser
import bibtexparser.middlewares as m
import bibtexparser.model as model
import re
from obsidown import utils

bibdict: dict[str, model.Entry] | None = None


class RemoveTitleCurly(m.BlockMiddleware):
    """I don't know why the library adds the curcly braces authomatically,
    this middleware just removees them
    """

    def transform_entry(self, entry, *args, **kwargs):
        entry["title"] = entry["title"].replace("{", "").replace("}", "")
        return entry


class CitationConvert(MdOperations):
    def __init__(self, bibfile: str):
        """Load the bib file and store it in the object.
        bibfile can be a string or a path to the bibfile!?
        """
        # use cache
        global bibdict
        if bibdict is not None:
            self.bib = bibdict
            return

        with open(bibfile, "r") as f:
            print(f"Loading bib file {bibfile}")
            string = f.read()

        layers = [
            RemoveTitleCurly(),
            m.SeparateCoAuthors(),  # Co-authors should be separated as list of strings
            m.SplitNameParts(),  # Individual Names should be split into first, von, last, jr parts
        ]

        db = bibtexparser.parse_string(string, append_middleware=layers)

        print(f"Parsed {len(db.blocks)} blocks, including:"
        f"\n\t{len(db.entries)} entries"
            f"\n\t{len(db.comments)} comments"
            f"\n\t{len(db.strings)} strings and"
            f"\n\t{len(db.preambles)} preambles")
        entries_dict = {}
        for entry in db.entries:
            entries_dict[entry.key] = entry

        self.bib = entries_dict
        bibdict = entries_dict

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the citations in the markdown file to a link citation format."""
        new_contents = file.contents
        citation_key_set: set[str] = set()

        def convert_to_citation(match):
            citation_key = match.group(1)
            citation_key_set.add(citation_key)

            key = citation_key
            if key not in self.bib:
                raise ValueError(f"Key {key} not found in the bib file")

            entry = self.bib[key]

            citation_string = f"({self._format_citation(entry)})"
            if "url" in entry:
                return f'[{citation_string}]({entry["url"]})'
            else:
                print(f"WARNING: No url in the bib entry {entry.key}")
                return f'[{citation_string}](/notes/{utils.to_kebab_case(file.get_title())}#{key})'  # this has a lot of dependencies, should be refactored

        new_contents = re.sub(
            r"\[\[@([^\]]+?)(\|([^\]]+))?\]\]",
            convert_to_citation,
            new_contents,
        )

        # Should add config to see if needs to add a section of references at the end
        if len(citation_key_set) != 0:
            new_contents += "\n\n# References\n\n"
        for i, key in enumerate(citation_key_set):
            entry = self.bib[key]
            new_contents += f"<p id={key}>[{i+1}] {self._format_long_citation(entry)}\n\n </p>\n"

        return MdFile(
            metadata=file.metadata,
            contents=new_contents,
            references=file.references,
            filename=file.filename,
        )

    def _format_citation(self, entry: model.Entry):
        """Prints a citation using APA style"""
        final_string = self._format_citation_name(entry)
        final_string += f" {self.__format_date(entry)}"
        final_string = (
            final_string.strip()
        )  # in case format_date returns an empty string

        return final_string

    def __format_date(self, entry: model.Entry):
        """Formats the date of the citation"""
        if "date" not in entry:
            if "year" in entry:
                result = entry["year"]
                if "month" in entry:
                    month = entry["month"]
                    result = f"{month.capitalize()}. {result}"
                return entry["year"]
            print(f"WARNING: No date nor year in the bib entry {entry.key}")
            return ""
        # assume is in the format of %Y-%m-%d, or %Y-%m or %Y
        date_str = entry["date"]
        date_list = date_str.split("-")
        year = date_list[0]
        return year

    def _format_citation_name(self, entry: model.Entry):
        """Formats the citation name"""
        if "author" not in entry:
            raise ValueError(f"No author in the bib entry {entry}")

        def join_name_parts(name_parts: list[str]) -> str:
            return " ".join(name_parts)

        authors: list[m.NameParts] = entry["author"]

        final_string = f"{join_name_parts(authors[0].last)}"
        if len(authors) == 1:
            pass
        elif len(authors) == 2:
            final_string += f" & {join_name_parts(authors[1].last)}"
        else:
            final_string += " et al."

        return final_string

    def _format_long_citation(self, entry: model.Entry):
        final_string = self._format_citation_name(entry)
        if "url" in entry:
            final_string += f" [“{entry['title']}”]({entry['url']})"
        else:
            final_string += f" “{entry['title']}”"

        final_string += f" {self.__format_journal_type(entry)}"
        final_string += f" {self.__format_date(entry)}"
        return final_string

    def __format_journal_type(self, entry: model.Entry):
        """Formats the journal citation type"""
        result = ""
        match entry.entry_type:
            case "article":
                result = self.__format_article(entry)
            case "book":
                result = self.__format_book(entry)
            case "inproceedings":
                result = self.__format_inproceedings(entry)
            case "online":
                result = self.__format_online(entry)
            case "misc":
                result = self.__format_misc(entry)
            case _:
                print(f"WARNING: Unknown type journal for {entry.key} - {entry.entry_type}")
            
        if result:
            # remove { and } from the result
            result = result.replace("{", "").replace("}", "")

        return result

    def __format_article(self, entry: model.Entry):
        """Formats the article citation type"""
        final_string = ""
        if "journal" in entry:
            final_string = f"{entry['journal']}"
        if "volume" in entry:
            final_string += f" Vol. {entry['volume']}"
        if "number" in entry:
            final_string += f"({entry['number']})"
        if "pages" in entry:
            final_string += f", pp. {entry['pages']}"

        return final_string

    def __format_book(self, entry: model.Entry):
        """Formats the book citation type"""
        return f"{entry['publisher']}"

    def __format_inproceedings(self, entry: model.Entry):
        if "publisher" in entry:
            string = f"{entry['publisher']} "
        elif "booktitle" in entry:
            string = f"{entry['booktitle']} "
        elif "eventtitle" in entry:
            string = f"{entry['eventtitle']} "
        else:
            print("WARNING: No publisher or booktitle in the bib entry")
            return " "

        return f"{string}"

    def __format_online(self, entry: model.Entry):
        if "eprinttype" not in entry:
            print(f"WARNING: {entry.key} has no eprinttype in the bib entry")
            return ""

        match entry["eprinttype"]:
            case "arxiv":
                return f"arXiv preprint arXiv:{entry['eprint']}"
            case "arXiv":
                return f"arXiv preprint arXiv:{entry['eprint']}"
            case "doi":
                return self._format_doi(entry)
            case _:
                print(f"WARNING: {entry.key} Unknown eprinttype for -{entry['eprinttype']}-")
                return ""

    def __format_misc(self, entry: model.Entry):
        if "publisher" in entry and "arxiv" in entry["publisher"].lower():
            return f"arXiv preprint arXiv:{entry['eprint']}"
        
        print(f"WARNING: No known misc in the bib entry {entry.key}")