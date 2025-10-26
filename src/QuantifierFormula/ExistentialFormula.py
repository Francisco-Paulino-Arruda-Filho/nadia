from QuantifierFormula.QuantifierFormula import QuantifierFormula


class ExistentialFormula(QuantifierFormula):
    def __init__(self, variable=None, formula=None):
      super().__init__( forAll = False, variable=variable, formula=formula)