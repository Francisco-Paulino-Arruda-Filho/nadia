from rply import ParserGenerator
from AtomFormula.AtomFormula import AtomFormula
from NegationFormula.NegationFormula import NegationFormula
from ParserInterface import ParserInterface
from BinaryFormula.AndFormula import AndFormula
from BinaryFormula.OrFormula import OrFormula
from BinaryFormula.ImplicationFormula import ImplicationFormula
from BinaryFormula.BiImplicationFormula import BiImplicationFormula
from BinaryFormula.BinaryFormula import BinaryFormula
from PredicatedFormula.PredicatedFormula import PredicateFormula
from QuantifierFormula.ExistentialFormula import ExistentialFormula
from QuantifierFormula.UniversalFormula import UniversalFormula
from models.lexer import Lexer

class ParserTheorem(ParserInterface):
    """
    Parser para teoremas no formato 'premissas ⊢ conclusão'
    Suporta: lista de premissas separadas por vírgula e conclusão
    """
    
    def __init__(self, state):
        super().__init__(state)
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['COMMA', 'OPEN_PAREN', 'CLOSE_PAREN', 'NOT',
             'AND', 'OR',  'BOTTOM','ATOM', 'IMPLIE', 'IFF',
             'VAR','EXT','ALL', 'V_DASH'],
            # The precedence $\lnot,\forall,\exists,\land,\lor,\rightarrow,\leftrightarrow$
            precedence=[
                ('right', ['IFF']),
                ('right', ['IMPLIE']),
                ('right', ['OR']),
                ('right', ['AND']),
                ('right', ['EXT']),
                ('right', ['ALL']),
                ('right', ['NOT']),
            ]
        )
        self._build_parser()

    def _build_parser(self):
        """Constrói as regras de produção do parser"""
        
        @self.pg.production('program : formulaslist V_DASH formula')
        @self.pg.production('program : V_DASH formula')
        def program(p):
            return self._handle_program(p)

        @self.pg.production('formula : EXT formula')
        @self.pg.production('formula : ALL formula')
        @self.pg.production('formula : formula OR formula')
        @self.pg.production('formula : formula AND formula')
        @self.pg.production('formula : formula IMPLIE formula')
        @self.pg.production('formula : formula IFF formula')
        @self.pg.production('formula : NOT formula')
        @self.pg.production('formula : ATOM OPEN_PAREN variableslist CLOSE_PAREN')
        @self.pg.production('formula : ATOM')
        @self.pg.production('formula : BOTTOM')
        def formula(p):
            return self._handle_formula(p)

        @self.pg.production('formula : OPEN_PAREN formula CLOSE_PAREN')
        def paren_formula(p):
            result = p[1]
            return p[0], result[1]

        @self.pg.production('variableslist : VAR')
        @self.pg.production('variableslist : VAR COMMA variableslist')
        def variablesList(p):
            return self._handle_variables_list(p)

        @self.pg.production('formulaslist : formula')
        @self.pg.production('formulaslist : formula COMMA formulaslist')
        def formulasList(p):
            return self._handle_formulas_list(p)

        @self.pg.error
        def error_handle(token):
            self._handle_error(token)

    def _handle_program(self, p):
        """Processa a estrutura principal do teorema (premissas ⊢ conclusão)"""
        if len(p) == 2:
            # Caso: ⊢ conclusão (sem premissas)
            self.result = ([], p[1][1])
            return [], p[1][1]
        else:
            # Caso: premissas ⊢ conclusão
            self.result = (p[0][1], p[2][1])
            return p[0][1], p[2][1]

    def _handle_formula(self, p):
        """Processa diferentes tipos de fórmulas (reutilizado do FormulaParser)"""
        if len(p) < 3:
            return self._handle_simple_formula(p)
        elif len(p) == 4:
            return self._handle_predicate_formula(p)
        elif len(p) == 3:
            return self._handle_binary_formula(p)
        
        raise ValueError("Estrutura de fórmula inválida")

    def _handle_simple_formula(self, p):
        """Processa fórmulas simples (átomos, negação, quantificadores)"""
        token = p[0]
        
        if token.gettokentype() == 'ATOM':
            return token, AtomFormula(key=token.value)
        elif token.gettokentype() == 'BOTTOM':
            return token, AtomFormula(key=token.value)
        elif token.gettokentype() == 'NOT':
            result = p[1]
            return token, NegationFormula(formula=result[1])
        else:
            # Quantificadores
            result1 = p[0]
            result2 = p[1]
            
            if token.gettokentype() == 'EXT':
                var = token.value.split('E')[1]
                return token, ExistentialFormula(variable=var, formula=p[1][1])
            elif token.gettokentype() == 'ALL':
                var = token.value.split('A')[1]
                return token, UniversalFormula(variable=var, formula=p[1][1])
            
        raise ValueError(f"Tipo de token não reconhecido: {token.gettokentype()}")

    def _handle_predicate_formula(self, p):
        """Processa fórmulas predicadas com variáveis"""
        varlist = p[2]
        return p[0], PredicateFormula(name=p[0].value, variables=varlist[1])

    def _handle_binary_formula(self, p):
        """Processa fórmulas binárias (conectivos)"""
        result1 = p[0]
        result2 = p[2]
        operator = p[1]
        
        operator_map = {
            '&': AndFormula,
            '|': OrFormula,
            '->': ImplicationFormula,
            '<->': BiImplicationFormula
        }
        
        formula_class = operator_map.get(operator.value)
        if formula_class:
            return result1[0], formula_class(left=result1[1], right=result2[1])
        else:
            return result1[0], BinaryFormula(
                key=operator.value, 
                left=result1[1], 
                right=result2[1]
            )

    def _handle_variables_list(self, p):
        """Processa lista de variáveis"""
        if len(p) == 1:
            return p[0], [p[0].value]
        else:
            result = p[2]
            return p[0], [p[0].value] + result[1]

    def _handle_formulas_list(self, p):
        """Processa lista de fórmulas (premissas)"""
        if len(p) == 1:
            return p[0], [p[0][1]]
        else:
            result = p[2]
            return p[0], [p[0][1]] + result[1]

    def _handle_error(self, token):
        """Trata erros de parsing"""
        productions = self.state.splitlines()
        error = ''  

        if not productions or productions == ['']:
            error = 'Nenhum teorema foi recebido, verifique a entrada.'
        elif token.gettokentype() == '$end':
            error = 'Nenhum teorema foi recebido, verifique a entrada.'
        else:
            source_position = token.getsourcepos()
            error = self._build_error_message(productions, source_position, token)
                
        raise ValueError(f"@@{error}")

    def _build_error_message(self, productions, source_position, token):
        """Constrói mensagem de erro detalhada"""
        error_lines = [
            'A definição do teorema não está correta.',
            'Formato esperado:',
            '  - "⊢ conclusão" (sem premissas)',
            '  - "premissa₁, premissa₂, ..., premissaₙ ⊢ conclusão"',
            '  - Use vírgulas para separar premissas',
            '',
            'Lembre-se que cada fórmula segue a BNF:',
            'F :== P | ~ P | P & Q | P | Q | P -> Q | P <-> Q | (P)',
            'onde P,Q são átomos, ou com quantificadores: ∀x F, ∃x F',
            '',
            'Erro de sintaxe:'
        ]
        
        error = '\n'.join(error_lines) + '\n'
        error += productions[source_position.lineno - 1] + '\n'
        
        # Adiciona indicador de posição
        error += ' ' * (source_position.colno - 1) + '^'
        
        if token.gettokentype() == 'OUT':
            error += ' Símbolo não pertence a linguagem.'
            
        return error

    def parse(self):
        """
        Executa o parsing do teorema
        
        Returns:
            Tupla (premissas, conclusão) onde:
            - premissas: lista de fórmulas
            - conclusão: fórmula
            
        Raises:
            ValueError: Se houver erro de sintaxe no teorema
        """
        return self._execute_parsing()

    def get_parser(self):
        """Retorna o parser construído"""
        return self.pg.build()

    def get_result(self):
        """Retorna o resultado do parsing"""
        return self.result

    def get_premisses(self):
        """Retorna apenas as premissas (conveniência)"""
        if self.result:
            return self.result[0]
        return []

    def get_conclusion(self):
        """Retorna apenas a conclusão (conveniência)"""
        if self.result:
            return self.result[1]
        return None

    @staticmethod
    def get_theorem(input_text=''):
        """
        Método estático para compatibilidade com código existente
        
        Args:
            input_text: Texto do teorema a ser parseado
            
        Returns:
            Tupla (premissas, conclusão) ou ([], None) em caso de erro
        """
        try:
            parser = ParserTheorem(input_text)
            return parser.parse()
        except ValueError:
            return [], None

    @staticmethod
    def to_string(premisses, conclusion, parentheses=False):
        """
        Converte teorema para string no formato padrão
        
        Args:
            premisses: Lista de fórmulas (premissas)
            conclusion: Fórmula (conclusão)
            parentheses: Se deve usar parênteses nas fórmulas
            
        Returns:
            String representando o teorema
        """
        if not premisses:
            return '|- ' + conclusion.toString(parentheses=parentheses)
        else:
            premisses_str = ", ".join(
                f.toString(parentheses=parentheses) for f in premisses
            )
            return f"{premisses_str} |- {conclusion.toString(parentheses=parentheses)}"

    @staticmethod
    def to_latex(premisses, conclusion, parentheses=False):
        """
        Converte teorema para LaTeX
        
        Args:
            premisses: Lista de fórmulas (premissas)
            conclusion: Fórmula (conclusão)
            parentheses: Se deve usar parênteses nas fórmulas
            
        Returns:
            String LaTeX representando o teorema
        """
        if not premisses:
            return '\\vdash ' + conclusion.toLatex(parentheses=parentheses)
        else:
            premisses_latex = ", ".join(
                f.toLatex(parentheses=parentheses) for f in premisses
            )
            return f"{premisses_latex} \\vdash {conclusion.toLatex(parentheses=parentheses)}"

    @staticmethod
    def is_valid_theorem(input_text):
        """
        Verifica se o texto é um teorema válido
        
        Args:
            input_text: Texto a ser verificado
            
        Returns:
            bool: True se é um teorema válido, False caso contrário
        """
        try:
            parser = ParserTheorem(input_text)
            premisses, conclusion = parser.parse()
            return conclusion is not None
        except ValueError:
            return False

    @staticmethod
    def parse_and_validate(input_text, expected_premisses_count=None):
        """
        Parseia e valida um teorema
        
        Args:
            input_text: Texto do teorema
            expected_premisses_count: Número esperado de premissas (opcional)
            
        Returns:
            dict: Resultado com informações de validação
        """
        try:
            parser = ParserTheorem(input_text)
            premisses, conclusion = parser.parse()
            
            result = {
                'valid': True,
                'premisses': premisses,
                'conclusion': conclusion,
                'premisses_count': len(premisses),
                'string_representation': ParserTheorem.to_string(premisses, conclusion),
                'latex_representation': ParserTheorem.to_latex(premisses, conclusion)
            }
            
            if expected_premisses_count is not None:
                result['expected_premisses_count'] = expected_premisses_count
                result['premisses_count_match'] = len(premisses) == expected_premisses_count
            
            return result
            
        except ValueError as e:
            error_msg = str(e)
            if "@@" in error_msg:
                error_msg = error_msg.split("@@")[-1]
                
            return {
                'valid': False,
                'error': error_msg,
                'premisses': [],
                'conclusion': None,
                'premisses_count': 0
            }