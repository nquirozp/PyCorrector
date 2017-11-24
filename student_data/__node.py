class _Node:
    def __init__(self, value=None):
        self.value = value
        self.after = None

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)
