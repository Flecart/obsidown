from obsidown import (
    convert_maths,
    convert_katex,
    convert_images,
    extract_links,
    convert_links,
    filter_link,
    remove_extension,
    convert_external_links,
)


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


def test_convert_katex():
    page = "No math here"
    expected_output = "No math here"
    assert convert_katex(page) == expected_output

    # page = "$$x = y \\\\ a$$ and $a = b$"
    # expected_output = "$$x = y \\\\\\ a$$ and $a = b$"
    # assert convert_katex(page) == expected_output

    # page = "$$x = y_{i}$$"
    # expected_output = "$$x = y\\_{i}$$"
    # assert convert_katex(page) == expected_output

    # page = "$$x = y_{i}$$ and $$x = y_{i}$$"
    # expected_output = "$$x = y\\_{i}$$ and $$x = y\\_{i}$$"

    # page = "$$x = y_{i}$$ and $$x = y_{i}$$ and $$x = y_{i}$$"
    # expected_output = "$$x = y\\_{i}$$ and $$x = y\\_{i}$$ and $$x = y\\_{i}$$"


def test_convert_images():
    base_url = "http://example.com/images"

    # Test case: Single image tag
    page = "![[image.png]]"
    expected_output = '<img src="http://example.com/images/image.png" alt="image">'
    assert convert_images(page, base_url) == expected_output

    # Test case: Multiple image tags
    page = "![[image1.jpeg]] and ![[image2.webp]]"
    expected_output = '<img src="http://example.com/images/image1.jpeg" alt="image1"> and <img src="http://example.com/images/image2.webp" alt="image2">'
    assert convert_images(page, base_url) == expected_output

    # Test case: No image tags
    page = "No images here"
    expected_output = "No images here"
    assert convert_images(page, base_url) == expected_output

    # Test case: Image tag with number
    page = "![[name.png|123]]"
    expected_output = (
        '<img src="http://example.com/images/name.png" width="123" alt="name">'
    )
    assert convert_images(page, base_url) == expected_output


def test_extract_links():
    # Test case: Single link
    page = "[[link1]]"
    expected_output = ["link1"]
    assert extract_links(page) == expected_output

    # Test case: Multiple links
    page = "[[link1]] and [[link2]]"
    expected_output = ["link1", "link2"]
    assert extract_links(page) == expected_output

    # Test case: No links
    page = "No links here"
    expected_output = []
    assert extract_links(page) == expected_output


def test_convert_links():
    base_url = "http://example.com"

    # Test case: Single link
    page = "[[link1]]"
    expected_output = "[link1](http://example.com/link1)"
    assert convert_links(page, base_url) == expected_output

    # Test case: Multiple links
    page = "[[link1]] and [[link2]]"
    expected_output = (
        "[link1](http://example.com/link1) and [link2](http://example.com/link2)"
    )
    assert convert_links(page, base_url) == expected_output

    # Test case: No links
    page = "No links here"
    expected_output = "No links here"
    assert convert_links(page, base_url) == expected_output

    # Test alias links
    page = "[[link1|alias1]] and [[link2|alias2]]"
    expected_output = (
        "[alias1](http://example.com/link1) and [alias2](http://example.com/link2)"
    )

    # Test kebab conversion
    page = "[[link with spaces]]"
    expected_output = "[link with spaces](http://example.com/link-with-spaces)"
    assert convert_links(page, base_url) == expected_output

    # Test hashtag mix conversion
    page = (
        "[[Legge di Coulomb#Principio di sovrapposizione|principio di sovrapposizione]]"
    )
    expected_output = "[principio di sovrapposizione](http://example.com/legge-di-coulomb#principio-di-sovrapposizione)"
    assert convert_links(page, base_url) == expected_output

    page = "[[#internal-link]]"
    expected_output = "[#internal-link](#internal-link)"
    assert convert_links(page, base_url) == expected_output


def test_filter_link():
    # Test case: Single link
    page = "Hello [[world]]"
    links = ["world"]
    expected_output = "Hello world"
    assert filter_link(page, links) == expected_output

    # Test case: Multiple links
    page = "Hello [[world]], [[Python]] is great"
    links = ["world", "Python"]
    expected_output = "Hello world, Python is great"
    assert filter_link(page, links) == expected_output

    # Test case: No links
    page = "Hello world"
    links = []
    expected_output = "Hello world"
    assert filter_link(page, links) == expected_output


def test_remove_extension():
    # Test case: Filename with extension
    filename = "file.txt"
    expected_output = "file"
    assert remove_extension(filename) == expected_output

    # Test case: Filename without extension
    filename = "file"
    expected_output = "file"
    assert remove_extension(filename) == expected_output

    # Test case: Filename with multiple dots
    filename = "my.file.txt"
    expected_output = "my.file"
    assert remove_extension(filename) == expected_output


def test_convert_external_links():
    # Test case: Single external link
    page = "https://google.com"
    expected_output = "[https://google.com](https://google.com)"
    assert convert_external_links(page) == expected_output

    # Test case: External link already in markdown format
    page = "[https://google.com](https://google.com)"
    expected_output = "[https://google.com](https://google.com)"
    assert convert_external_links(page) == expected_output

    # Test case: Multiple external links
    page = "https://google.com and https://github.com"
    expected_output = "[https://google.com](https://google.com) and [https://github.com](https://github.com)"
    assert convert_external_links(page) == expected_output

    # Test case: No external links
    page = "No links here"
    expected_output = "No links here"
    assert convert_external_links(page) == expected_output

    page = "[https://csunibo.github.io/tecnologie-web/lucidi/teoria/23-metadati.pdf](https://csunibo.github.io/tecnologie-web/lucidi/teoria/23-metadati.pdf)"
    expected_output = "[https://csunibo.github.io/tecnologie-web/lucidi/teoria/23-metadati.pdf](https://csunibo.github.io/tecnologie-web/lucidi/teoria/23-metadati.pdf)"
    assert convert_external_links(page) == expected_output

    page = "[video](https://youtu.be/D5ABGSplM8c?t=548&autoplay=1)"
    expected_output = "[video](https://youtu.be/D5ABGSplM8c?t=548&autoplay=1)"
    assert convert_external_links(page) == expected_output

    page = "[(Shannon 1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)"
    expected_output = "[(Shannon 1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)"
    assert convert_external_links(page) == expected_output

    page = "[qui](https://mbernste.github.io/posts/vae/#appendix-derivation-of-the-kl-divergence-term-when-the-variational-posterior-and-prior-are-gaussian)"
    expected_output = "[qui](https://mbernste.github.io/posts/vae/#appendix-derivation-of-the-kl-divergence-term-when-the-variational-posterior-and-prior-are-gaussian)"
    assert convert_external_links(page) == expected_output

    page = "[Esperimento didattico: portabilità dei compilatori](https://so.v2.cs.unibo.it/wiki/index.php/Esperimento_didattico:_portabilit%C3%A0_dei_compilatori)"
    expected_output = "[Esperimento didattico: portabilità dei compilatori](https://so.v2.cs.unibo.it/wiki/index.php/Esperimento_didattico:_portabilit%C3%A0_dei_compilatori)"
    assert convert_external_links(page) == expected_output

    page = "[wiki](https://it.wikipedia.org/wiki/Sistema_di_numerazione_posizionale#:~:text=Un%20sistema%20di%20numerazione%20posizionale,posizione%20che%20occupano%20nella%20notazione.)"
    expected_output = "[wiki](https://it.wikipedia.org/wiki/Sistema_di_numerazione_posizionale#:~:text=Un%20sistema%20di%20numerazione%20posizionale,posizione%20che%20occupano%20nella%20notazione.)"
    assert convert_external_links(page) == expected_output
