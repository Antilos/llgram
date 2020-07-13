class Rule:
    def __init__(self):
        """
        """
        self.left = ""
        self.right = list()
        self.first = set()

    def __repr__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __str__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __eq__(self, other):
        return str(self) == str(other)

    def getLeft(self):
        return self.left

    def setLeft(self, val):
        self.left = val
    
    def getRight(self):
        return self.right

    def appendRight(self, val):
        self.right.append(val)

    def getFirst(self):
        return self.first

    def addFirst(self, val):
        self.first.add(val)

    def setFirst(self, val):
        self.first = val