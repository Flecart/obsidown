"""Convert a citation format to a link citation format."""

from obsidown.operations.base import MdFile, MdOperations
import bibtexparser
import bibtexparser.middlewares as m
import bibtexparser.model as model
import re

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
            string = f.read()

        layers = [
            RemoveTitleCurly(),
            m.SeparateCoAuthors(),  # Co-authors should be separated as list of strings
            m.SplitNameParts(),  # Individual Names should be split into first, von, last, jr parts
        ]

        db = bibtexparser.parse_string(string, append_middleware=layers)

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

            return citation_string

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
        final_string += f" {self.__format_date(entry)}"
        final_string = (
            final_string.strip()
        )  # in case format_date returns an empty string

        return final_string

    def __format_date(self, entry: model.Entry):
        """Formats the date of the citation"""
        if "date" not in entry:
            print(f"WARNING: No date in the bib entry {entry.key}")
            return ""
        # assume is in the format of %Y-%m-%d, or %Y-%m or %Y
        date_str = entry["date"]
        date_list = date_str.split("-")
        year = date_list[0]
        return year

    def _format_citation_name(self, entry: model.Entry):
        """Formats the citation name"""
        if "author" not in entry:
            raise ValueError("No author in the bib entry")

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

        match entry.entry_type:
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
        final_string = ""
        if "journaltitle" in entry:
            final_string = f"{entry['journaltitle']}"
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
