from Factory.RuleBase import RuleBase

class WrongDef(RuleBase):
    """
    Classe para representar regras inválidas ou com erro de sintaxe.
    Usada para capturar e reportar erros nas produções do parser.
    """
    
    def __init__(self, line: str, formula):
        self._line = line
        self._formula = formula
        self._is_copied = False

    @property
    def line(self) -> str:
        return self._line

    @property
    def formula(self):
        return self._formula

    @property
    def is_copied(self) -> bool:
        return self._is_copied

    @is_copied.setter
    def is_copied(self, value: bool) -> None:
        self._is_copied = value

    def evaluation(self, parser, deduction_result) -> None:
        """
        Não faz nenhuma avaliação pois esta é uma regra inválida.
        O erro já foi reportado durante o parsing.
        """
        return

    def toLatex(self, symbol_table) -> str:
        """
        Retorna uma representação LaTeX para a regra inválida.
        Normalmente isso não será usado, mas é implementado por consistência.
        """
        if self._formula:
            return f'\\text{{ERRO: {self._formula.toString()}}}'
        return '\\text{ERRO: Regra inválida}'

    def __str__(self) -> str:
        return f"WrongDef(line={self.line}, formula={self.formula})"

    def __repr__(self) -> str:
        return self.__str__()