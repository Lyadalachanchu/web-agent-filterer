from bs4 import BeautifulSoup
from bs4.element import Comment, NavigableString, Tag
from typing import List, Optional


class Leaf:
    """
    Represents a visible text node in the HTML DOM with methods to traverse and extract context.
    """
    
    def __init__(self, element: NavigableString):
        """
        Initialize a Leaf with a BeautifulSoup NavigableString element.
        
        Args:
            element: A BeautifulSoup NavigableString (text node)
        """
        self._element = element
        self.text = element.strip()
    
    @property
    def parent(self) -> Tag:
        """Get the BeautifulSoup parent element."""
        return self._element.parent
    
    def go_up(self, n: int) -> Optional[Tag]:
        """
        Get the ancestor element n levels up.
        
        Args:
            n: Number of levels to go up (0 = immediate parent, 1 = grandparent, etc.)
            
        Returns:
            The ancestor Tag element, or None if it doesn't exist
        """
        current = self._element.parent
        for _ in range(n):
            if current.parent is None:
                return None
            current = current.parent
        return current
    
    def get_other_leaves_from_ancestor(self, n: int) -> List['Leaf']:
        """
        Go up n steps in the DOM tree and get all leaves from that ancestor.
        
        Args:
            n: Number of levels to go up (0 = immediate parent, 1 = grandparent, etc.)
            
        Returns:
            List of Leaf objects found under the ancestor (including self)
        """
        ancestor = self.go_up(n)
        if ancestor is None:
            return []
        
        # Find all text nodes under this ancestor
        other_leaves = []
        for element in ancestor.find_all(string=True):
            # Check if it's visible
            if _is_visible(element):
                other_leaves.append(Leaf(element))
        
        return other_leaves
    
    def get_context(self, levels_up: int = 1, pretty: bool = False) -> str:
        """
        Get HTML context by going n levels up.
        
        Args:
            levels_up: Number of levels to go up
            pretty: Whether to prettify the HTML output
            
        Returns:
            HTML string of the ancestor element
        """
        ancestor = self.go_up(levels_up)
        if ancestor is None:
            return ""
        
        if pretty:
            return ancestor.prettify()
        return str(ancestor)
    
    def get_parent_tag(self) -> str:
        """Get the tag name of the immediate parent."""
        return self.parent.name
    
    def has_parent_tag(self, tag_name: str) -> bool:
        """Check if the immediate parent has a specific tag."""
        return self.parent.name == tag_name.lower()
    
    def __str__(self) -> str:
        text_preview = self.text[:30] + "..." if len(self.text) > 30 else self.text
        return f"Leaf: '{text_preview}' in <{self.get_parent_tag()}>"
    
    def __repr__(self) -> str:
        text_preview = self.text[:20] + "..." if len(self.text) > 20 else self.text
        return f"Leaf(text='{text_preview}', parent_tag='{self.get_parent_tag()}')"


def _is_visible(element: NavigableString) -> bool:
    """
    Check if a text element is visible.
    
    Args:
        element: A BeautifulSoup NavigableString
        
    Returns:
        True if the element is visible, False otherwise
    """
    if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    if not element.string or not element.string.strip():
        return False
    return True


def extract_leaves(html_file: str) -> List[Leaf]:
    """
    Extract all visible text nodes from an HTML file as Leaf objects.
    
    Args:
        html_file: Path to the HTML file
        
    Returns:
        List of Leaf objects representing visible text nodes
    """
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    
    leaves = []
    for element in soup.find_all(string=True):
        if _is_visible(element):
            leaves.append(Leaf(element))
    
    return leaves


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