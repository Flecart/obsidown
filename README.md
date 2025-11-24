# ObsiDown

Convert obsidian files into well linked markdowns!

## Example use cases
- Export Obsidian subdirectories while maintaining the links in markdown format
- Make obsidian math Kramdown-compatible
- Use obsidian to write for Jekyll web pages. 

## How to use

Define a configuration file `config.yaml`. In the repo it is provided one as example.
Install the `poetry` dependencies and then you just need to run `poetry run python -m obsidown --config path/to/config.yaml`

It's possible to install from `pypi` index by `pip install obsidown`.
Then you can run it with `python -m obsidown`

## Feedback

This project is a hobby project used to automate some things I use myself. Currently it is a early early project!
If you need additional features or report some issues or need help, feel free to open a new issue.

## Documentation

The quickest way to check what is the format of the config file is to see the pydantic from `config.py`.
Here I will just outline it briefly.

- `sources` defines where to look for the input files.
  - `paths`: where to look for the md files?
  - `images`: where to look for the linked images?
- `output` defines where to write the exported files.
  - `base`: defines the base url for links
  - `path`: defines a subpath for the markdown files
  - `images`: defines a subpath for the image fiiles
  - `filesystem`: where to write
- `pipeline`: defines the single operations possible on a markdown file.
  - `name`: the identifier of the operation, you should check `dispatch.py` for a list of the operations.
  - `options`: variable options of the single operation.

### Configuration Reference

Below is a more complete configuration example that you can adapt to your vault:

```yaml
sources:
  paths:
    - /path/to/obsidian/notes
  images:
    - /path/to/obsidian/assets
output:
  base: notes
  path: content/notes
  images: images/notes
  images_path: static/images/notes
  filesystem: /var/www/my-site
pipeline:
  - name: remove_after_string
    options:
      string: "# Private Section"
  - name: remove_single_char_lines
    options:
      character: "-"
  - name: update_frontmatter
    options:
      frontmatter:
        ShowToc: true
        TocOpen: false
  - name: link_convert
    options: {}
  - name: write_file
    options: {}
```

Some useful pipeline operations and their options:

- `remove_after_string`: drop content after the first occurrence of `string`. Set `line: true` to remove just the matching line portion.
- `remove_single_char_lines`: remove lines entirely made of repetitions of a single `character` (for example Obsidian separators like `-----`).
- `update_frontmatter`: merge or override metadata by passing a `frontmatter` dictionary.
- `citation_convert`: convert citations with `bibfile` pointing to a Zotero/BibTeX export.
- `link_convert`: translate Obsidian `[[wikilinks]]` into absolute links according to `output.base`.
- `write_file`: persisting step that writes the transformed file in the configured destination.

You can chain as many operations as you need; each one receives the output of the previous step, so ordering matters.