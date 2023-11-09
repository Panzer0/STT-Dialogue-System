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


def interpret_date(
    date_string: str, source_time: datetime = datetime.now()
) -> datetime:
    cal = pdt.Calendar()
    adjusted_date = replace_verbal_numbers(date_string)
    return cal.parseDT(adjusted_date, sourceTime=source_time)


def generate_verbal_path(path):
    directory, filename = os.path.split(path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_verbal{extension}"
    new_path = os.path.join(directory, new_filename)
    return new_path


NUMBER_DICT = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "twenty-first": 21,
    "twenty-second": 22,
    "twenty-third": 23,
    "twenty-fourth": 24,
    "twenty-fifth": 25,
    "twenty-sixth": 26,
    "twenty-seventh": 27,
    "twenty-eighth": 28,
    "twenty-ninth": 29,
    "thirtieth": 30,
    "thirty-first": 31,
}


def verbal_to_number(verbal_number: str, number_dict=NUMBER_DICT) -> str:
    if verbal_number in number_dict:
        return str(number_dict[verbal_number])
    else:
        return verbal_number


def replace_verbal_numbers(input_string: str, number_dict=NUMBER_DICT) -> str:
    words = input_string.split()
    for i in range(len(words)):
        if words[i].lower() in number_dict:
            words[i] = verbal_to_number(words[i].lower())
    return " ".join(words)


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
    print(interpret_date("Let's schedule it for August 2")[0])
