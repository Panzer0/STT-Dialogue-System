class DialogueOption:
    def __init__(self, input, output):
        """
        Initialize a new DialogueOption

        Parameters:
        - input:    A set of words that can result in the  DialogueOption
        - output:   A dict that describes the given DialogueOption
        """
        self.input = input
        self.output = output

    def