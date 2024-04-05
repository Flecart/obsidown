# ObsiDown

Convert obsidian files into well linked markdowns!

## Example use cases
- Export Obsidian subdirectories while maintaining the links in markdown format
- Make obsidian math Kramdown-compatible
- Use obsidian to write for Jekyll web pages. 

## How to use

Define a configuration file `config.yaml`. In the repo it is provided one as example.
Install the `poetry` dependencies and then you just need to run `poetry run python -m obsidown --config path/to/config.yaml`

Installation as a python package is still on todo!

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