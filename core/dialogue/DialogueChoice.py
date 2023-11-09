import os
import re
import json
from typing import Set


def contains_word(text: str, word: str):
    """
    Check if a string contains a given word

    Parameters:
        text (str): The string to check
        word (str): The word the presence of which is checked

    Returns:
        bool: True if the word is contained in text, False otherwise
    """
    return re.search(r"\b" + word + r"\b", text)


def generate_verbal_path(path: str) -> str:
    directory, filename = os.path.split(path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_verbal{extension}"
    new_path = os.path.join(directory, new_filename)
    return new_path


class DialogueChoice:
    def __init__(
        self,
        json_path: str = None,
        json_key: str = None,
        json_value: str = None,
        keywords: Set[str] = None,
        successor: "DialogueNode" = None,
    ):
        self.json_path = json_path
        self.json_path_verbal = (
            generate_verbal_path(json_path) if json_path else None
        )
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

    def erase_json(self, json_path: str, json_key: str) -> None:
        with open(json_path, "r+") as json_file:
            data = json.load(json_file)
            if json_key in data:
                del data[json_key]
                json_file.seek(0)
                json_file.truncate()
                json.dump(data, json_file, indent=4)

    def erase_all_json(self) -> None:
        if not (self.json_path and self.json_key and self.json_value):
            return
        try:
            self.erase_json(self.json_path, self.json_key)
            self.erase_json(self.json_path_verbal, self.json_key)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"An error occurred: {e}")

    def __update_json(self, path: str, key: str, value: str) -> None:
        try:
            with open(path, "r+") as json_file:
                data = json.load(json_file)
                data[key] = value
                json_file.seek(0)
                json_file.truncate()
                json.dump(data, json_file, indent=4)

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"An error occurred: {e}")
            with open(path, "w") as json_file:
                data = {key: value}
                json.dump(data, json_file, indent=4)

    def activate(self, answer: str = None) -> None:
        if self.json_path and self.json_key and self.json_value:
            self.__update_json(self.json_path, self.json_key, self.json_value)
            self.__update_json(self.json_path_verbal, self.json_key, answer)


if __name__ == "__main__":
    print(generate_verbal_path("path/to/file.json"))
