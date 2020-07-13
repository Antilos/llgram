class Rule:
    def __init__(self):
        """
        """
        self.left = ""
        self.right = list()
        self.first = set()
        self.action = None

    def __repr__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __str__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.__str__())

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

    def getAction(self):
        return self.action
    
    def setAction(self, val):
        self.action = val