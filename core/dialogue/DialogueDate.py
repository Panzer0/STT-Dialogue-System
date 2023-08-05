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


def interpret_date(date_string: str):
    now = datetime.now()
    cal = pdt.Calendar()
    return cal.parseDT(date_string, sourceTime=now)


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
        self.json_key_verbal = json_key + '_verbal'
        self.keywords = keywords if keywords is not None else set()
        self.successor = successor

    # todo: is_mentioned is hardly a suitable name given the changes.
    def is_mentioned(self, text: str) -> bool:
        """
        Check if a string contains any keywords

        Parameters:
            text (str): The string to check

        Returns:
            bool: True if a keyword is contained in text, False otherwise
        """
        keyword_used = any(contains_word(text, word) for word in self.keywords)
        date, status = interpret_date(text)
        is_valid_date = status == 1 and date > datetime.now()
        return (keyword_used or not self.keywords) and is_valid_date

    def __update_json(self, date_string: str):
        try:
            with open(self.json_path, "r+") as json_file:
                data = json.load(json_file)
                data[self.json_key] = interpret_date(date_string)[0]
                data[self.json_key_verbal] = date_string
                json_file.seek(0)
                json.dump(data, json_file, default=str)

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(self.json_path, "w") as json_file:
                data = {
                    self.json_key: interpret_date(date_string)[0],
                    self.json_key_verbal: date_string
                }
                json.dump(data, json_file, default=str)

    def activate(self, date_string: str) -> None:
        if self.json_path and self.json_key:
            self.__update_json(date_string)

if __name__ == '__main__':
    print(interpret_date("tomorrow")[1])