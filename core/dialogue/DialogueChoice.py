import re
import DialogueNode
import json
from typing import Set


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


class DialogueChoice:
    def __init__(
        self,
        json_path: str = None,
        json_key: str = None,
        json_value: str = None,
        keywords: Set[str] = None,
        successor: DialogueNode = None,
    ):
        self.json_path = json_path
        self.json_key = json_key
        self.json_value = json_value
        self.keywords = keywords if keywords is not None else set()
        self.successor = successor

    def is_mentioned(self, text: str) -> bool:
        """
        Check if a string contains any keywords

        Parameters:
            text (str): The string to check

        Returns:
            bool: True if a keyword is contained in text, False otherwise
        """
        return any(contains_word(text, word) for word in self.keywords)

    def __update_json(self):
        try:
            with open(self.json_path, "r+") as json_file:
                print(f"UPDATING FILE WITH KEY {self.json_key} AND VALUE {self.json_value}")
                data = json.load(json_file)
                data[self.json_key] = self.json_value
                json_file.seek(0)
                json_file.truncate()
                print(f"Dumping {data}")
                json.dump(data, json_file)

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"An error occurred: {e}")
            with open(self.json_path, "w") as json_file:
                data = {self.json_key: self.json_value}
                json.dump(data, json_file)

    def activate(self, answer: str = None) -> None:
        if self.json_path and self.json_key and self.json_value:
            self.__update_json()
