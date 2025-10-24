from models.BinaryFormula import BinaryFormula


class OrFormula(BinaryFormula):
    def __init__(self, left = None, right = None):
        super().__init__(key = '|', left=left, right = right)