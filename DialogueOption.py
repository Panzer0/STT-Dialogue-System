import re


def contains_word(text: str, word: str) -> None:
    """
    Check if a string contains a given word

    Parameters:
        text (str): The string to check
        word (str): The word the presence of which is checked

    Returns:
        bool: True if the word is contained in text, False otherwise
    """
    return re.search(r"\b" + word + r"\b", text)

# todo: Decouple definition dicts from keywords. 
# todo:     How to do this without making the class itself pointless? 
class DialogueOption:
    def __init__(self, name, keywords: set, definition: dict = None):
        """
        Initialize a new DialogueOption

        Parameters:
            keywords (set): A set of words that can result in the DialogueOption
            definition (dict): A dict that describes the given DialogueOption
        """
        self.name = name
        self.keywords = keywords
        self.definition = definition

    def is_mentioned(self, text: str) -> bool:
        """
        Check if a string contains any keywords

        Parameters:
            text (str): The string to check

        Returns:
            bool: True if a keyword is contained in text, False otherwise
        """
        return any(contains_word(text, word) for word in self.keywords)