from bs4 import BeautifulSoup
from bs4.element import Comment

def extract_parent_html_of_leaves(html_file):
    """
    Given an HTML file path, return a list of parent HTML blocks for all visible leaf text nodes.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")

    def is_visible(element):
        if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
            return False
        if isinstance(element, Comment):
            return False
        if not element.string or not element.string.strip():
            return False
        return True

    parent_html_list = []
    for element in soup.find_all(string=True):
        if is_visible(element):
            parent_html_list.append(str(element.parent))

    return parent_html_list