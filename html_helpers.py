from bs4 import BeautifulSoup
from bs4.element import Comment

def extract_leaves(html_text):
    """
    Given HTML text, return a list of leaf text nodes (no child tags).
    Filters out empty strings, comments, and script/style content.
    """
    soup = BeautifulSoup(html_text, "html.parser")

    def is_visible(element):
        # Remove scripts, styles, comments
        if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
            return False
        if isinstance(element, Comment):
            return False
        if not element.string or not element.string.strip():
            return False
        return True

    leaves = [element.string.strip() for element in soup.find_all(string=True) if is_visible(element)]
    return leaves