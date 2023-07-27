from typing import Set
import DialogueChoice


class DialogueNode:
    def __init__(self, choices: Set, default_choice=None):
        self.choices = choices
        self.default_choice = default_choice

    def advance(self, answer: str) -> "DialogueNode":
        # todo: Rethink the naming convention. "Selected choice" is a pleonasm.
        selected_choice = self.default_choice
        for choice in self.choices:
            if choice.is_mentioned(answer):
                selected_choice = choice
                break
        if selected_choice:
            selected_choice.activate()
            return selected_choice.successor
        return self
