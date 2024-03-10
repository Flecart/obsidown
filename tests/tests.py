import pytest
from obsidian_jekyll import convert_maths

def test_convert_maths():
    # Test case: Single math expression
    page = "$x = y$"
    expected_output = "$$x = y$$"
    assert convert_maths(page) == expected_output

    # Test case: Multiple math expressions
    page = "$x = y$ and $a = b$"
    expected_output = "$$x = y$$ and $$a = b$$"
    assert convert_maths(page) == expected_output

    # Test case: No math expressions
    page = "No math here"
    expected_output = "No math here"
    assert convert_maths(page) == expected_output

    # Test case: Multiple $$ dollars
    page = "$$\nx = y\n$$"
    expected_output = "\n$$\nx = y\n$$\n"
    assert convert_maths(page) == expected_output

    # Test case: Multiple $$ without endlines
    page = "$$x = y$$"
    expected_output = "$$x = y$$"
    assert convert_maths(page) == expected_output

    # Test case: Mixed $$ and $ dollars
    page = "$$\nx = y\n$$ and $a = b$"
    expected_output = "\n$$\nx = y\n$$\n and $$a = b$$"
    assert convert_maths(page) == expected_output