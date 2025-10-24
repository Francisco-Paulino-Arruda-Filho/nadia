from models.QuantifierFormula import QuantifierFormula


class UniversalFormula(QuantifierFormula):
    def __init__(self, variable=None, formula=None):
      super().__init__( forAll = True, variable=variable, formula=formula)