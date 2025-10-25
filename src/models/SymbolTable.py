from Defs.Defs import PremisseDef


class SymbolTable:

    def toString(self):
      for i in range(len(self.symbol_table)):
        print(self.symbol_table['scope_{}'.format(i)])

    def len_symbol_table(self):
      r = 0
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          r+=1
      return r

    def find_token(self, line):
      for i in range(len(self.symbol_table)):
        for j in range(len(self.symbol_table['scope_{}'.format(i)]['rules'])):
          if (self.symbol_table['scope_{}'.format(i)]['rules'][j].line==line):
            return self.symbol_table['scope_{}'.format(i)]['lines'][j]
      return None


    def check_is_visible(self, formula1_line, formula2_line):
      #Find formula1_line scope.
      if (int(formula1_line) <= int(formula2_line)): 
        return False
      current_scope = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_scope = self.symbol_table['scope_{}'.format(i)]
            break
        if current_scope is not None: 
          break
      #Check if formula2_line in formula1_line scope 
      while current_scope is not None:
        for rule in current_scope['rules']:
          if rule and (rule.line == formula2_line):
            return True
        current_scope = self.symbol_table[current_scope['parent']] if 'parent' in current_scope else None
      return False

    def find_scope(self, line):
        for key, scope in self.symbol_table.items():
            for rule in scope['rules']:
                if rule and (rule.line == line):
                    return key 
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, scope in self.symbol_table.items():
          if(int(scope['start_line'])==int(line)):
            return key

        return None

    # Returns True if the scope variable of the line is a fresh variable, i.e., it did not occur before this scope. 
    def is_fresh_variable(self, line):
      current_scope = self.find_scope(line)
      variable = self.symbol_table[current_scope]['variable'] if current_scope is not None else None
      return variable not in self.get_free_variables_before_scope(line)

    def get_free_variables_before_scope(self, line):
      free_variables = set()
      #Find formula1_line scope.
      scope = self.find_scope(line)
      scope = self.symbol_table[scope]['parent'] if scope in self.symbol_table else None
      while scope is not None:
          for rule in self.symbol_table[scope]['rules']:
            if (int(rule.line) < int(line)):
              free_variables = free_variables.union(rule.formula.free_variables())
            #Adds the variable for the universal introduction rule, i.e., if the line does not have a formula
            if (int(self.symbol_table[scope]['start_line'])<int(line) and self.symbol_table[scope]['variable']):
              free_variables = free_variables.union(set(self.symbol_table[scope]['variable']))
          scope = self.symbol_table[scope]['parent']
      return free_variables

    def get_visible_lines(self, formula1_line):
      #Find formula1_line scope.
      lines = []
      current_scope = None
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if rule and (rule.line == formula1_line):
            current_scope = self.symbol_table['scope_{}'.format(i)]
            break
        if current_scope is not None: 
          break
      #Check if formula2_line in formula1_line scope 
      while current_scope is not None:
        for rule in current_scope['rules']:
          if rule and (int(rule.line) < int(formula1_line)):
            lines.append(rule.line)
        current_scope = self.symbol_table[current_scope['parent']] if current_scope['parent'] else None
      return lines
      
      
    def getPremisses(self):
      lines = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseDef) ):
            lines.append(rule.line)
      return lines

    def getPremissesFormulas(self):
      formulas = []
      for i in range(len(self.symbol_table)):
        for rule in self.symbol_table['scope_{}'.format(i)]['rules']:
          if(isinstance(rule, PremisseDef) and rule.formula not in formulas):
            formulas.append(rule.formula)
      return formulas

    def getConclusionFormula(self):
      if self.symbol_table["scope_0"]["rules"][-1]:
        return self.symbol_table["scope_0"]["rules"][-1].formula
      else:
        return None
    
    def theoremToString(self,parentheses=False):
      premissas = sorted([p.toString(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premissas)+' |- '+fConclusion.toString(parentheses=parentheses))

    def theoremToLatex(self,parentheses=False):
      premisses = ([p.toLatex(parentheses=parentheses) for p in self.getPremissesFormulas()])
      fConclusion = self.getConclusionFormula()
      if(fConclusion):
        return (', '.join(premisses)+' \\vdash '+fConclusion.toLatex(parentheses=parentheses))

    def set_lines_visible(self):
        self.line_visible_lines = {}
        n = self.len_symbol_table()
        for i in range(1,n):
          self.line_visible_lines[str(i)] = self.get_visible_lines(str(i))



    def __init__(self):
        self.line_visible_lines = {}
        self.symbol_table = {
            'scope_0': {
                'name': 'scope_0',
                'parent': None,
                'rules': [],
                'lines': [],
                'variable': None,
                'start_line': '1', #Robson Não estava presente
                'end_line': '1'
            }
        }
        self.current_scope = 'scope_0'

    def insert(self, symbol, line):
        self.symbol_table[self.current_scope]['rules'].append(symbol)
        self.symbol_table[self.current_scope]['lines'].append(line)

    def start_scope(self, scope):
        self.current_scope = scope

    def end_scope(self, end_line):
        self.symbol_table[self.current_scope]['end_line'] = end_line
        if(self.symbol_table[self.current_scope]['parent'] is not None):
            self.current_scope = self.symbol_table[self.current_scope]['parent']

    def add_scope(self, start_line, variable=None):
        scope = 'scope_{}'.format(len(self.symbol_table))
        self.symbol_table[scope] = {
            'name': scope,
            'parent': self.current_scope,
            'rules': [],
            'lines': [],
            'variable': variable,
            'start_line': start_line,
            'end_line': start_line#Robson, não ser start_line        
            }
        self.start_scope(scope)

    def find_scope_variable(self, line):
        scope = self.find_scope(line)
        if scope is not None:
          return self.symbol_table[scope]['variable']
        #Verifica se a linha não tem fórmula (introdução do universal)
        for key, scope in self.symbol_table.items():
          if(int(scope['start_line'])==int(line)):
            return scope['variable']          
        return None

    def check_scope_is_valid(self, scope):
        current_scope = self.current_scope
        while current_scope is not None:
            if current_scope == scope:
                return True
            current_scope = self.symbol_table[current_scope]['parent']
        return False

    def lookup_formula_by_line(self, symbol_line, line):
        scope = self.find_scope(symbol_line)
        while scope is not None:
            for rule in self.symbol_table[scope]['rules']:
                if rule.line == line:
                    return rule.formula
            scope = self.symbol_table[scope]['parent']
        return None

    def check_scope_delimiter(self, line1, line2):
        for key, scope in self.symbol_table.items():
            if key != 'scope_0':
                if(scope['start_line'] == line1 and scope['end_line'] == line2):
                    start_rule = scope['rules'][0].formula if scope['rules'][0] is not None else None
                    end_rule = scope['rules'][-1].formula if scope['rules'][-1] is not None else None
                    return (start_rule, end_rule)
        return None, None

    def get_box_start(self):
        if self.current_scope != 'scope_0':
            return self.symbol_table[self.current_scope]['start_line']
        return None

    def get_box_end(self):
        if self.current_scope != 'scope_0':
            return self.symbol_table[self.current_scope]['end_line']
        return None             

    def get_first_rule_from_scope(self, line):
        scope = self.find_scope(line)
        if self.symbol_table[scope]['rules']==[]: 
          return None
        return self.symbol_table[scope]['rules'][0]
   
    def get_last_rule_from_scope(self):
        if self.symbol_table[self.current_scope]['rules']==[]: 
          return None
        return self.symbol_table[self.current_scope]['rules'][-1]

    def get_rule(self, rule_line):
        for key, scope in self.symbol_table.items():
            for key, line in enumerate(scope['lines']):
                if line.value == rule_line:
                    return scope['rules'][key]
        return None

    def count_formulas_by_end_box(self, line):
        for key, scope in self.symbol_table.items():
            if key != 'scope_0':
                if(scope['end_line'] == line):
                    return (line - int(scope['start_line']))
        return 0