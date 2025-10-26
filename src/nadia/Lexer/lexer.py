from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        #Comma
        self.lexer.add('COMMA', r'\,')

        # Dot
        self.lexer.add('DOT', r'\.')

        # Parentheses
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')

        #Brackets
        self.lexer.add('OPEN_BRACKET', r'\{')
        self.lexer.add('CLOSE_BRACKET', r'\}')

        # Vdash
        self.lexer.add('V_DASH', r'\|-|\|=')

        #rules
        self.lexer.add('IMP_INTROD', r'->i')
        self.lexer.add('IMP_ELIM', r'->e')
        self.lexer.add('OR_INTROD', r'\|i')
        self.lexer.add('OR_ELIM', r'\|e')
        self.lexer.add('AND_INTROD', r'&i')
        self.lexer.add('AND_ELIM', r'&e')
        self.lexer.add('NEG_INTROD', r'~i')
        self.lexer.add('NEG_ELIM', r'~e')
        self.lexer.add('RAA', r'raa')
        self.lexer.add('BOTTOM_ELIM', r'@e')
        self.lexer.add('COPY', r'copie')

        # Connectives
        self.lexer.add('BOTTOM', r'@')
        self.lexer.add('NOT', r'~')
        self.lexer.add('AND', r'&')
        self.lexer.add('OR', r'\|')
        self.lexer.add('IMPLIE', r'->')
        self.lexer.add('IFF', r'<->')

        #First order rules
        self.lexer.add('EXT_INTROD', r'Ei')
        self.lexer.add('EXT_ELIM', r'Ee')
        self.lexer.add('ALL_INTROD', r'Ai')
        self.lexer.add('ALL_ELIM', r'Ae')

        #First order connectives
        self.lexer.add('EXT', r'E[a-z][a-z0-9]*')
        self.lexer.add('ALL', r'A[a-z][a-z0-9]*')

        # definitions
        self.lexer.add('DEF_NOT', r'def\~')
        self.lexer.add('DEF_IMPLIE', r'def\->')
        self.lexer.add('DEF_AND', r'def\&')
        self.lexer.add('DEF_OR', r'def\|')
        self.lexer.add('DEF_IFF', r'def\<->')
        self.lexer.add('DEF_BASE', r'defAtomos')

        # Dash
        self.lexer.add('DASH', r'-')

        # Number
        self.lexer.add('NUM', r'\d+')

        #justification
        self.lexer.add('HYPOTHESIS', r'hip')
        self.lexer.add('PREMISE', r'pre')

        #Variable
        self.lexer.add('VAR', r'(?!pre|hip)[a-z][a-z0-9]*')

        # Atom
        self.lexer.add('ATOM', r'[A-Z][A-Z0-9]*' )

        # Ignore spaces and comments
        self.lexer.ignore('##[^##]*##')
        self.lexer.ignore('#[^\n]*\n?')
        self.lexer.ignore('\s+')  

        # Detect symbols out of grammar
        self.lexer.add('OUT', r'.*' )      

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()