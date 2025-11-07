class LatexBuilder:
    """
    Builder para construção de código LaTeX para provas lógicas.
    Implementa o padrão Builder para encapsular a lógica de formatação LaTeX.
    """
    
    def __init__(self):
        self.latex = "\\begin{logicproof}{6}\n"
        self._subproof_depth = 0
    
    def add_premise(self, formula):
        self.latex += f"{formula.toLatex()} & premissa\\\\\n"
        return self
    
    def add_hypothesis(self, formula, variable=None):
        if variable:
            self.latex += f"\\llap{{${variable}\\quad$}}{formula.toLatex()} & hipótese\\\\\n"
        else:
            self.latex += f"{formula.toLatex()} & hipótese\\\\\n"
        return self
    
    def add_hypothesis_variable_only(self, variable):
        self.latex += f"\\llap{{${variable}\\quad$}} &\\\\\n"
        return self
    
    def begin_subproof(self):
        self.latex += "\\begin{subproof}\n"
        self._subproof_depth += 1
        return self
    
    def end_subproof(self):
        if self._subproof_depth > 0:
            self.latex = self.latex[:-3] + '\n'
            self.latex += "\\end{subproof}\n"
            self._subproof_depth -= 1
        return self
    
    def add_negation_elimination(self, formula, ref1, ref2):
        self.latex += f"{formula.toLatex()} & $\\lnot e$ {ref1}, {ref2}\\\\\n"
        return self
    
    def add_implication_elimination(self, formula, ref1, ref2):
        self.latex += f"{formula.toLatex()} & $\\rightarrow e$ {ref1}, {ref2}\\\\\n"
        return self
    
    def add_implication_introduction(self, formula, start, end):
        self.latex += f"{formula.toLatex()} & $\\rightarrow i$ {start}-{end}\\\\\n"
        return self
    
    def add_disjunction_introduction(self, formula, ref):
        self.latex += f"{formula.toLatex()} & $\\lor i$ {ref}\\\\\n"
        return self
    
    def add_conjunction_introduction(self, formula, ref1, ref2):
        self.latex += f"{formula.toLatex()} & $\\land i$ {ref1},{ref2}\\\\\n"
        return self
    
    def add_conjunction_elimination(self, formula, ref):
        self.latex += f"{formula.toLatex()} & $\\land e$ {ref}\\\\\n"
        return self
    
    def add_disjunction_elimination(self, formula, ref, start1, end1, start2, end2):
        self.latex += f"{formula.toLatex()} & $\\lor e$ {ref}, {start1}-{end1}, {start2}-{end2}\\\\\n"
        return self
    
    def add_negation_introduction(self, formula, start, end):
        self.latex += f"{formula.toLatex()} & $\\lnot i$ {start}-{end}\\\\\n"
        return self
    
    def add_bottom_elimination(self, formula, ref):
        self.latex += f"{formula.toLatex()} & $\\bot e$ {ref}\\\\\n"
        return self
    
    def add_raa(self, formula, start, end):
        self.latex += f"{formula.toLatex()} & raa {start}-{end}\\\\\n"
        return self
    
    def add_copy(self, formula, ref):
        self.latex += f"{formula.toLatex()} & copie {ref}\\\\\n"
        return self
    
    def add_forall_elimination(self, formula, ref):
        self.latex += f"{formula.toLatex()} & $\\forall e$ {ref}\\\\\n"
        return self
    
    def add_exists_introduction(self, formula, ref):
        self.latex += f"{formula.toLatex()} & $\\exists i$ {ref}\\\\\n"
        return self
    
    def add_exists_elimination(self, formula, ref, start, end):
        self.latex += f"{formula.toLatex()} & $\\exists e$ {ref},{start}-{end}\\\\\n"
        return self
    
    def add_forall_introduction(self, formula, start, end):
        self.latex += f"{formula.toLatex()} & $\\forall i$ {start}-{end}\\\\\n"
        return self
    
    def build(self):
        result = self.latex[:-3] if self.latex.endswith('\\\\\n') else self.latex
        result += '\n\\end{logicproof}'
        return result
    
    def reset(self):
        self.latex = "\\begin{logicproof}{6}\n"
        self._subproof_depth = 0
        return self
    
    def get_current_latex(self):
        return self.latex