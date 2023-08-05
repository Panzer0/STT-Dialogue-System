# todo: This mirrors much of DialogueChoice. Rework with inheritance at mind?
import json
import re
from typing import Set

import parsedatetime as pdt
from datetime import datetime

import DialogueNode


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


class DialogueDate:
    def __init__(
        self,
        json_path: str = None,
        json_key: str = None,
        keywords: Set[str] = None,
        successor: DialogueNode = None,
    ):
        self.json_path = json_path
        self.json_key = json_key
        self.keywords = keywords
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

    def __update_json(self, date_string: str):
        try:
            with open(self.json_path, "r+") as json_file:
                data = json.load(json_file)
                data[self.json_key] = self.__interpret_date(date_string)
                json_file.seek(0)
                json.dump(data, json_file)

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(self.json_path, "w") as json_file:
                data = {self.json_key: self.__interpret_date(date_string)}
                json.dump(data, json_file, default=str)

    def __interpret_date(self, date_string: str):
        now = datetime.now()
        cal = pdt.Calendar()
        parsed_date, _ = cal.parseDT(date_string, sourceTime=now)
        return parsed_date

    # todo: DialogueChoice's activate takes no arguments. This might pose a
    # todo: challenge if I decide to go for inheritance.
    def activate(self, date_string: str) -> None:
        if self.json_path and self.json_key:
            self.__update_json(date_string)
