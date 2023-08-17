from typing import Set

from core.dialogue.DialogueChoice import DialogueChoice


class DialogueNode:
    def __init__(self, choices: Set, default_choice=None, back_keywords: Set[str] = None, prompt: str = ""):
        self.choices = choices
        self.default_choice = default_choice
        self.back_choice = DialogueChoice(keywords=back_keywords) if back_keywords else None
        self.prompt = prompt

    def advance(self, answer: str) -> "DialogueNode":
        # todo: Rethink the naming convention. "Selected choice" is a pleonasm.
        selected_choice = self.default_choice
        combined_choices = set(self.choices)
        if self.back_choice is not None:
            combined_choices.add(self.back_choice)

        for choice in combined_choices:
            if choice.is_mentioned(answer):
                selected_choice = choice
                break

        if selected_choice:
            selected_choice.activate(answer)
            return selected_choice.successor
        return self

    def __str__(self):
        return self.prompt
