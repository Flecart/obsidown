import re

def convert_maths(page: str) -> str:
    """ Replaces all occurrences of $maths$ with $$\nmathematics$$\n 
    Tipical of obsidian pages into correct kramdown markdown latex.
    """
    return re.sub(r"\$(.*?)\$", r"$$\n\1\n$$", page)

