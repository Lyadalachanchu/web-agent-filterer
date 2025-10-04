from typing import Dict, Any


class ContextFilterer:
    """Filters and formats browser context for the agent."""
    
    def __init__(self, token_budget: int):
        self.token_budget = token_budget
    
    def to_markdown(self, raw: Dict[str, Any], goal: str = "") -> str:
        """Convert raw browser data to markdown observation."""
        # Extract key information from raw data
        md_parts = []
        
        if "url" in raw:
            md_parts.append(f"**URL:** {raw['url']}\n")
        
        if "title" in raw:
            md_parts.append(f"**Title:** {raw['title']}\n")
        
        # Extract text from accessibility tree if available
        if "ax" in raw and raw["ax"]:
            ax_text = self._extract_ax_text(raw["ax"])
            if ax_text:
                max_content_len = 3000
                if len(ax_text) > max_content_len:
                    ax_text = ax_text[:max_content_len] + "..."
                md_parts.append(f"**Page Content:**\n{ax_text}\n")
        
        if "error" in raw:
            md_parts.append(f"**Error:** {raw['error']}\n")
        
        if "success" in raw:
            md_parts.append(f"**Success:** {raw['success']}\n")
        
        return "\n".join(md_parts) if md_parts else "No observation available."
    
    def _extract_ax_text(self, ax_node: Dict[str, Any], depth: int = 0) -> str:
        """Extract readable text from accessibility tree."""
        if not ax_node or depth > 10:
            return ""
        
        texts = []
        if "name" in ax_node and ax_node["name"]:
            # Skip repetitive role names
            if ax_node.get("role") not in ["LineBreak"]:
                texts.append(ax_node["name"])
        
        if "children" in ax_node:
            for child in ax_node["children"]:
                child_text = self._extract_ax_text(child, depth + 1)
                if child_text:
                    texts.append(child_text)
        
        return " ".join(texts)

