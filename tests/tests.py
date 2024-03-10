import pytest
from obsidian_jekyll import convert_maths, convert_images

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

def test_convert_images():
    base_url = "http://example.com/images"

    # Test case: Single image tag
    page = '![[image.png]]'
    expected_output = '<img src="http://example.com/images/image.png" alt="image">'
    assert convert_images(page, base_url) == expected_output

    # Test case: Multiple image tags
    page = '![[image1.jpeg]] and ![[image2.webm]]'
    expected_output = '<img src="http://example.com/images/image1.jpeg" alt="image1"> and <img src="http://example.com/images/image2.webm" alt="image2">'
    assert convert_images(page, base_url) == expected_output

    # Test case: No image tags
    page = "No images here"
    expected_output = "No images here"
    assert convert_images(page, base_url) == expected_output

    # Test case: Image tag with number
    page = '![[name.png|123]]'
    expected_output = '<img src="http://example.com/images/name.png" width="123" alt="name">'
    assert convert_images(page, base_url) == expected_output