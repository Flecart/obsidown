"""Convert a citation format to a link citation format."""

from obsidown.operations.base import MdFile, MdOperations
import bibtexparser
import bibtexparser.middlewares as m
import bibtexparser.model as model
import re


def __entries_to_dict(entries):
    entries_dict = {}
    for entry in entries:
        entries_dict[entry.key] = entry
    return entries_dict


class CitationConvert(MdOperations):
    def __init__(self, bibfile: str):
        """Load the bib file and store it in the object.
        bibfile can be a string or a path to the bibfile!?
        """
        with open(bibfile, "r") as f:
            string = f.read()

        layers = [
            m.SeparateCoAuthors(),  # Co-authors should be separated as list of strings
            m.SplitNameParts(),  # Individual Names should be split into first, von, last, jr parts
        ]

        db = bibtexparser.parse_string(string, append_middleware=layers)

        self.bib = __entries_to_dict(db.entries)

    def __call__(self, file: MdFile) -> MdFile:
        """Converts the citations in the markdown file to a link citation format."""
        new_contents = file.contents
        citation_key_list: list[str] = []

        def convert_to_citation(match):
            citation_key = match.group(1)
            citation_key_list.append(citation_key)

            key = citation_key
            if key not in self.bib:
                raise ValueError(f"Key {key} not found in the bib file")

            entry = self.bib[key]

            citation_string = self._format_citation(entry)
            if "url" in entry:
                return f'[{citation_string}]({entry["url"]})'

            return citation_string

        new_contents = re.sub(
            r"\[\[(@[^\]]+?)\]\]",
            convert_to_citation,
            new_contents,
        )

        # Should add config to see if needs to add a section of references at the end
        new_contents += "\n\n# References\n\n"
        for i, key in enumerate(citation_key_list):
            entry = self.bib[key]
            new_contents += f"[{i+1}] {self._format_long_citation(entry)}\n\n"

        return MdFile(
            metadata=file.metadata,
            contents=new_contents,
            references=file.references,
            filename=file.filename,
        )

    def _format_citation(self, entry: model.Entry):
        """Prints a citation using APA style"""
        final_string = self._format_citation_name(entry)
        if "date" in entry:
            # assume is in the format of %Y-%m-%d, or %Y-%m or %Y
            date_str = entry["date"]
            date_list = date_str.split("-")
            year = date_list[0]
            final_string += f" ({year})"

    def _format_date(self, entry: model.Entry):
        """Formats the date of the citation"""
        if "date" not in entry:
            raise ValueError("No date in the bib entry")

        date_str = entry["date"]
        date_list = date_str.split("-")
        year = date_list[0]
        return year

    def _format_citation_name(self, entry: model.Entry):
        """Formats the citation name"""
        if "author" not in entry:
            raise ValueError("No author in the bib entry")

        authors: list[m.NameParts] = entry["author"]

        final_string = f"{authors[0].last}"
        if len(authors) == 2:
            final_string += f" & {authors[1].last}"
        else:
            final_string += " et al."

        return final_string

    def _format_long_citation(self, entry: model.Entry):
        final_string = self._format_citation_name(entry)
        if "url" in entry:
            final_string += f" [“{entry['title']}”]({entry['url']})"
        else:
            final_string += f" “{entry["title"]}”"

        final_string += f" {self.__format_journal_type(entry)}"
        final_string += f" {self._format_date(entry)}"
        return final_string

    def __format_journal_type(self, entry: model.Entry):
        """Formats the journal citation type"""

        match entry.type:
            case "article":
                return self.__format_article(entry)
            case "book":
                return self.__format_book(entry)
            case "inproceedings":
                return self.__format_inproceedings(entry)
            case "online":
                return self.__format_online(entry)
            case _:
                print("WARNING: Unknown type journal")
                return ""

    def __format_article(self, entry: model.Entry):
        """Formats the article citation type"""
        return f"{entry['journaltitle']} {entry['volume']}/{entry['number']}, {entry['pages']}"

    def __format_book(self, entry: model.Entry):
        """Formats the book citation type"""
        return f"{entry['publisher']}"

    def __format_inproceedings(self, entry: model.Entry):
        if "publisher" in entry:
            string = f"{entry['publisher']} "
        else:
            string = f"{entry['booktitle']} "

        return f"{string}"

    def __format_online(self, entry: model.Entry):
        if "eprinttype" not in entry:
            print("WARNING: No eprinttype in the bib entry")
            return ""

        match entry["eprinttype"]:
            case "arxiv":
                return f"arXiv preprint arXiv:{entry['eprint']}"
            case "doi":
                return self._format_doi(entry)
            case _:
                print("WARNING: Unknown eprinttype")
                return ""
