from rply import ParserGenerator
from AtomFormula.AtomFormula import AtomFormula
from NegationFormula.NegationFormula import NegationFormula
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.BiImplicationFormula import BiImplicationFormula
from BinaryFormula.BinaryFormula import BinaryFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.OrFormula import OrFormula
from nadia.Lexer.lexer import Lexer

class ParserFormula:
    def __init__(self, state):
        self.state = state
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            [
                "COMMA",
                "OPEN_PAREN",
                "CLOSE_PAREN",
                "NOT",
                "AND",
                "OR",
                "BOTTOM",
                "ATOM",
                "IMPLIE",
                "IFF",
                "VAR",
                "EXT",
                "ALL",
            ],
            # The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ("right", ["IFF"]),
                ("right", ["IMPLIE"]),
                ("right", ["OR"]),
                ("right", ["AND"]),
                ("right", ["EXT"]),
                ("right", ["ALL"]),
                ("right", ["NOT"]),
            ],
        )

    def parse(self):
        @self.pg.production("program : formula")
        def program(p):
            return p[0][1]

        @self.pg.production("formula : EXT formula")
        @self.pg.production("formula : ALL formula")
        @self.pg.production("formula : formula OR formula")
        @self.pg.production("formula : formula AND formula")
        @self.pg.production("formula : formula IMPLIE formula")
        @self.pg.production("formula : formula IFF formula")
        @self.pg.production("formula : NOT formula")
        @self.pg.production("formula : ATOM OPEN_PAREN variableslist CLOSE_PAREN")
        @self.pg.production("formula : ATOM")
        @self.pg.production("formula : BOTTOM")
        def formula(p):
            if len(p) < 3:
                if p[0].gettokentype() == "ATOM":
                    return p[0], AtomFormula(key=p[0].value)
                elif p[0].gettokentype() == "BOTTOM":
                    return p[0], AtomFormula(key=p[0].value)
                elif p[0].gettokentype() == "NOT":
                    result = p[1]
                    return p[0], NegationFormula(formula=result[1])
                elif type(p[0]) is not tuple:
                    result1 = p[0]
                    result2 = p[1]
                    # Universal Formula
                    if p[0].gettokentype() == "EXT":
                        var = p[0].value.split("E")[1]
                        return p[0], ExistentialFormula(variable=var, formula=p[1][1])
                    elif p[0].gettokentype() == "ALL":
                        var = p[0].value.split("A")[1]
                        return p[0], UniversalFormula(variable=var, formula=p[1][1])
            elif len(p) == 4:
                # Predicate Formula
                varlist = p[2]
                return p[0], PredicateFormula(name=p[0].value, variables=varlist[1])
            elif len(p) == 3:
                # Binary Formula
                result1 = p[0]
                result2 = p[2]
                if p[1].value == "&":
                    return result1[0], AndFormula(left=result1[1], right=result2[1])
                elif p[1].value == "|":
                    return result1[0], OrFormula(left=result1[1], right=result2[1])
                elif p[1].value == "->":
                    return result1[0], ImplicationFormula(
                        left=result1[1], right=result2[1]
                    )
                elif p[1].value == "<->":
                    return result1[0], BiImplicationFormula(
                        left=result1[1], right=result2[1]
                    )
                else:
                    return result1[0], BinaryFormula(
                        key=p[1].value, left=result1[1], right=result2[1]
                    )

        @self.pg.production("formula : OPEN_PAREN formula CLOSE_PAREN")
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production("variableslist : VAR")
        @self.pg.production("variableslist : VAR COMMA variableslist")
        def variablesList(p):
            if len(p) == 1:
                return p[0], [p[0].value]
            else:
                result = p[2]
            return p[0], [p[0].value] + result[1]

        @self.pg.error
        def error_handle(token):
            productions = self.state.splitlines()
            error = ""

            if productions == [""]:
                error = "Nenhuma fórmula foi recebida, verifique a entrada."
            if token.gettokentype() == "$end":
                error = "Nenhuma fórmula foi recebida, verifique a entrada."
            else:
                source_position = token.getsourcepos()
                error = "A definição da fórmula não está correta, verifique se todas regras foram aplicadas corretamente.\nLembre-se que uma uma fórmula é definida pela seguinte BNF:\nF :== P | ~ P | P & Q | P | Q | P -> Q | P <-> Q | (P), onde P,Q são átomos.\n"
                error += "Erro de sintaxe:\n"
                error += productions[source_position.lineno - 1]
                string = "\n"
                for i in range(source_position.colno - 1):
                    string += " "
                string += "^"
                if token.gettokentype() == "OUT":
                    string += " Símbolo não pertence a linguagem."
                error += string

            raise ValueError("@@" + error)

    def get_error(self, type_error, token_error, rule):
        productions = self.state.splitlines()
        column_error = token_error.getsourcepos().colno
        erro = "Erro de sintaxe na linha {}:\n".format(
            token_error.getsourcepos().lineno
        )
        erro += productions[token_error.getsourcepos().lineno - 1] + "\n"
        for i in range(column_error - 1):
            erro += " "

        return erro

    def get_parser(self):
        return self.pg.build()

    @staticmethod
    def getFormula(input_text=""):
        try:
            lexer = Lexer().get_lexer()
            tokens = lexer.lex(input_text)

            pg = ParserFormula(state=input_text)
            pg.parse()
            parser = pg.get_parser()
            result = parser.parse(tokens)
            return result
        except ValueError:
            return None
        else:
            return None
            pass
