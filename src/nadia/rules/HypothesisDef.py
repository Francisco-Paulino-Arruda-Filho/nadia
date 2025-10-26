hypothesis = {}

def limpaHipotese():
    global hypothesis
    hypothesis = {}


class HypothesisDef():
    def __init__(self, line, formula):
        self.line = line
        self.formula = formula
        self.copied = None
        self.is_copied = False

    def evaluation(self, parser, deduction_result):
        return

    def toLatex(self, symbol_table):
        line = self.copied if self.copied else self.line
        if line not in hypothesis:
            hypothesis[line] = str(len(hypothesis) + 1)
        latex = '\\big['+self.formula.toLatex()+'\\big]^{_{'+hypothesis[line]+'}}'
        return latex
