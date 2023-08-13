from typing import Set


class DialogueNode:
    def __init__(self, choices: Set, default_choice=None, prompt: str = "", predecessor = ):
        self.choices = choices
        self.default_choice = default_choice
        self.prompt = prompt

    def advance(self, answer: str) -> "DialogueNode":
        # todo: Rethink the naming convention. "Selected choice" is a pleonasm.
        selected_choice = self.default_choice
        for choice in self.choices:
            if choice.is_mentioned(answer):
                selected_choice = choice
                break
        if selected_choice:
            selected_choice.activate(answer)
            return selected_choice.successor
        return self

    def __str__(self):
        return self.prompt
