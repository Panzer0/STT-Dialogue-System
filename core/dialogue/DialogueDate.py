# todo: This mirrors much of DialogueChoice. Rework with inheritance at mind?
import json
import os
import re
from typing import Set

import parsedatetime as pdt
from datetime import datetime


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



def interpret_date(date_string: str, source_time=datetime.now()):
    cal = pdt.Calendar()
    return cal.parseDT(date_string, sourceTime=source_time)


def generate_verbal_path(path):
    directory, filename = os.path.split(path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_verbal{extension}"
    new_path = os.path.join(directory, new_filename)
    return new_path


class DialogueDate:
    def __init__(
        self,
        json_path: str = None,
        json_key: str = None,
        keywords: Set[str] = None,
        successor: "DialogueNode" = None,
    ):
        self.json_path = json_path
        self.json_path_verbal = (
            generate_verbal_path(json_path) if json_path else None
        )
        self.json_key = json_key
        self.json_key_verbal = json_key + "_verbal"
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

    def erase_json(self, json_path, json_key):
        with open(json_path, "r+") as json_file:
            data = json.load(json_file)
            if json_key in data:
                del data[json_key]
                json_file.seek(0)
                json_file.truncate()
                json.dump(data, json_file, indent=4)

    def erase_all_json(self):
        if not (self.json_path and self.json_key):
            return
        try:
            self.erase_json(self.json_path, self.json_key)
            self.erase_json(self.json_path_verbal, self.json_key)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"An error occurred: {e}")

    def __update_json(self, path, key, value):
        try:
            with open(path, "r+") as json_file:
                data = json.load(json_file)
                data[key] = value
                json_file.seek(0)
                json_file.truncate()
                json.dump(data, json_file, default=str, indent=4)

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"An error occurred: {e}")
            with open(path, "w") as json_file:
                data = {key: value}
                json.dump(data, json_file, default=str, indent=4)

    def activate(self, date_string: str) -> None:
        if self.json_path and self.json_key:
            self.__update_json(
                self.json_path, self.json_key, interpret_date(date_string)[0]
            )
            self.__update_json(
                self.json_path_verbal, self.json_key, date_string
            )


if __name__ == "__main__":
    print(interpret_date("How about in a week?")[0])
