"""
Web Agent HTML Query Generator

This module transforms web agent sub-goals into HTML-optimized queries
for embedding-based retrieval of relevant HTML snippets.

Approach:
1. Take a sub-goal (e.g., "Click the contact button in navigation")
2. Use OpenAI to transform it into an HTML-centric description
3. The query describes expected HTML structure, tags, attributes, and content
4. When embedded, this query will have high cosine similarity with matching HTML

Example:
    Sub-goal: "Click the contact button"
    Query: "navigation menu anchor link with href contact, button or link element 
            with text 'Contact', clickable navigation item"
"""

import os
from openai import OpenAI
from typing import Optional
import dotenv
dotenv.load_dotenv()

# Initialize OpenAI client
client = OpenAI()


def subgoal_to_html_query(
    subgoal: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3
) -> str:
    """
    Transform a web agent sub-goal into an HTML-optimized query.
    
    This function uses OpenAI's LLM to convert task-oriented descriptions
    into queries that describe the HTML structure, making them more suitable
    for embedding-based retrieval of HTML snippets.
    
    Args:
        subgoal: The web agent's sub-goal (e.g., "Click the submit button")
        model: OpenAI model to use for transformation
        temperature: Controls randomness (lower = more focused)
    
    Returns:
        An HTML-centric query string optimized for embedding similarity
    
    Example:
        >>> subgoal_to_html_query("Fill in the email field in the contact form")
        "contact form input field with type email, text input element with 
         placeholder or label for email address, form field with name or id 
         containing email"
    """
    
    system_prompt = """You are an expert at analyzing web interactions and HTML structure.

Your task is to transform web automation sub-goals into queries that describe the HTML elements involved.

When given a sub-goal, output a query that describes:
1. HTML tags/elements that would be used (button, input, a, form, etc.)
2. Relevant attributes (class, id, href, type, placeholder, etc.)
3. Text content that might appear
4. Structural context (navigation, form, header, etc.)

The query should sound like a description of HTML code, NOT like a task description.

Examples:

Sub-goal: "Click the contact button in the navigation menu"
Query: "navigation menu anchor link or button element with text Contact, nav item with href to contact page, clickable navigation link with class nav-link or similar"

Sub-goal: "Fill in the email field in the contact form"  
Query: "contact form input element with type email, text input field with email related name id or placeholder, form field labeled email address"

Sub-goal: "Submit the form"
Query: "form submit button element, input or button with type submit, form submission button with text like Submit or Send"

Sub-goal: "Find the company's phone number"
Query: "text content displaying phone number format, contact information section with phone tel link, element containing formatted telephone number"

Rules:
- Focus on HTML structure, tags, and attributes
- Use terms that would appear in actual HTML code
- Keep it under 50 words
- No action verbs (click, fill, submit) - describe the elements, not actions
- Include multiple variations of how it might be coded"""

    user_prompt = f"""Sub-goal: "{subgoal}"

Convert this into an HTML-focused query:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=150
        )
        
        query = response.choices[0].message.content.strip()
        
        # Remove any "Query:" prefix if the model included it
        if query.lower().startswith("query:"):
            query = query[6:].strip()
            
        return query
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback: return a basic transformation
        return f"HTML element for {subgoal}"


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Get embedding vector for a text string.
    
    Args:
        text: Text to embed
        model: OpenAI embedding model to use
    
    Returns:
        List of floats representing the embedding vector
    """
    if text is None:
        return None
    text = str(text).replace("\n", " ")
    resp = client.embeddings.create(input=[text], model=model)
    return resp.data[0].embedding


def subgoal_to_embedding(
    subgoal: str,
    transform: bool = True,
    embedding_model: str = "text-embedding-3-small",
    llm_model: str = "gpt-4o-mini"
) -> tuple[list[float], str]:
    """
    Convert a web agent sub-goal to an embedding vector.
    
    This is the main function for the web agent pipeline. It:
    1. Transforms the sub-goal into an HTML query (optional)
    2. Embeds the query
    3. Returns both the embedding and the query used
    
    Args:
        subgoal: The web agent's sub-goal
        transform: Whether to transform via LLM (recommended) or embed directly
        embedding_model: Model for creating embeddings
        llm_model: Model for query transformation
    
    Returns:
        Tuple of (embedding_vector, query_used)
    
    Example:
        >>> embedding, query = subgoal_to_embedding("Click the login button")
        >>> print(query)
        "button element with text Login, input or button for authentication, 
         login form submit button"
        >>> len(embedding)
        1536
    """
    if transform:
        # Transform sub-goal into HTML-optimized query
        query = subgoal_to_html_query(subgoal, model=llm_model)
        print(f"Transformed sub-goal → query:")
        print(f"  '{subgoal}' →")
        print(f"  '{query}'")
    else:
        query = subgoal
    
    # Get embedding
    embedding = get_embedding(query, model=embedding_model)
    
    return embedding, query


def batch_subgoals_to_embeddings(
    subgoals: list[str],
    transform: bool = True,
    embedding_model: str = "text-embedding-3-small",
    llm_model: str = "gpt-4o-mini"
) -> list[tuple[list[float], str]]:
    """
    Process multiple sub-goals in batch.
    
    Args:
        subgoals: List of sub-goal strings
        transform: Whether to transform via LLM
        embedding_model: Model for embeddings
        llm_model: Model for transformation
    
    Returns:
        List of (embedding, query) tuples
    """
    results = []
    for i, subgoal in enumerate(subgoals, 1):
        print(f"\n[{i}/{len(subgoals)}] Processing: {subgoal}")
        embedding, query = subgoal_to_embedding(
            subgoal, 
            transform=transform,
            embedding_model=embedding_model,
            llm_model=llm_model
        )
        results.append((embedding, query))
    
    return results


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("WEB AGENT HTML QUERY GENERATOR")
    print("=" * 80)
    
    # Test cases - typical web agent sub-goals
    test_subgoals = [
        "Click the contact button in the navigation",
        "Fill in the email field in the contact form",
        "Click on the About Us link",
        "Find the company's address",
        "Submit the newsletter subscription form",
        "Navigate to the services page",
        "Click the first portfolio item",
        "Find the search bar in the header",
    ]
    
    print("\n📋 Test Sub-goals:")
    for i, sg in enumerate(test_subgoals, 1):
        print(f"  {i}. {sg}")
    
    print("\n" + "=" * 80)
    print("TRANSFORMATION EXAMPLES")
    print("=" * 80)
    
    # Show a few detailed examples
    for subgoal in test_subgoals[:3]:
        print(f"\n{'─' * 80}")
        print(f"Sub-goal: {subgoal}")
        print(f"{'─' * 80}")
        
        embedding, query = subgoal_to_embedding(subgoal, transform=True)
        
        print(f"\n✓ Generated Query:")
        print(f"  {query}")
        print(f"\n✓ Embedding shape: {len(embedding)} dimensions")
        print(f"✓ First 5 values: {embedding[:5]}")
    
    print("\n" + "=" * 80)
    print("COMPARISON: WITH vs WITHOUT TRANSFORMATION")
    print("=" * 80)
    
    test_goal = "Click the contact button"
    
    print(f"\nSub-goal: '{test_goal}'")
    
    print("\n[WITHOUT transformation]")
    embedding_direct, query_direct = subgoal_to_embedding(
        test_goal, 
        transform=False
    )
    print(f"Query used: '{query_direct}'")
    
    print("\n[WITH transformation]")
    embedding_transformed, query_transformed = subgoal_to_embedding(
        test_goal,
        transform=True
    )
    print(f"Query used: '{query_transformed}'")
    
    print("\n💡 The transformed query is much more likely to match HTML snippets!")
    print("   It describes structure, tags, and attributes rather than actions.")
    
    print("\n" + "=" * 80)
    print("USAGE IN WEB AGENT PIPELINE")
    print("=" * 80)
    print("""
# In your web agent:

from make_query import subgoal_to_embedding
import numpy as np

# 1. Get sub-goal from agent
subgoal = agent.get_current_subgoal()  # e.g., "Click login button"

# 2. Convert to embedding
query_embedding, query_text = subgoal_to_embedding(subgoal, transform=True)

# 3. Find most similar HTML snippet (using cosine similarity)
similarities = np.dot(html_embeddings, query_embedding)
best_match_idx = np.argmax(similarities)
relevant_html = html_snippets[best_match_idx]

# 4. Agent uses the HTML snippet
agent.execute_action(relevant_html)
    """)
    
    print("\n✅ All tests complete!")

