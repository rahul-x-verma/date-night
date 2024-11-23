from langchain_core.tools import tool

@tool
def find_restaurant(cuisine: str) -> str:
    """Returns the name of a restaurant in Brooklyn that serves the given cuisine.

    Args:
        cuisine: The type of cuisine to search for.
    """
    if cuisine == "Italian":
        return "Misi, Williamsburg"
    if cuisine == "Japanese":
        return "Sushi Lin, Prospect Heights"
    if cuisine == "Indian":
        return "Mint Heights, Fort Greene"
    if cuisine == "Korean":
        return "Cote, Koreatown"
    if cuisine == "Thai":
        return "Amy Thai, Prospect Lefferts Gardens"
    if cuisine == "American":
        return "Junior's Diner"
    else:
        return "Dekalb Food Market"
