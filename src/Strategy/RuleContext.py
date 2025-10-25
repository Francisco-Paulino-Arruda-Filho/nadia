class RuleContext:
    """Contexto que contém os dados necessários para validação"""
    def __init__(self, symbol_table, line, formula, references, hypothesis=None):
        self.symbol_table = symbol_table
        self.line = line
        self.hypothesis = hypothesis
        self.formula = formula
        self.references = references  # Lista de referências
        self.errors = []