import argparse

from .main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts Obsidian notes to markdown export")
    parser.add_argument("--config", type=str, help="The config file", default="config.yaml")
    args = parser.parse_args()

    main(args.config)