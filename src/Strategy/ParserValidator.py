from models.constants import constants

class ParserValidator:
    def __init__(self, parser, deduction_result):
        self.parser = parser
        self.deduction_result = deduction_result
    
    def validate_references(self, rule_def):
        """Valida todas as referências de uma regra (equivalente ao código original)"""
        # 1. Verificar se referências ocorrem antes da regra
        before_ok = self._check_line_reference_before_rule_error(rule_def)
        if not before_ok:
            return False
        
        # 2. Verificar se referências estão no escopo
        self._check_line_scope_reference_error(rule_def)
        
        # 3. Verificar escopo para regras que usam caixas
        if self._needs_scope_validation(rule_def):
            self._check_scope_reference_error(rule_def)
            
        return True
    
    def _check_line_reference_before_rule_error(self, rule_def):
        """Verifica se todas as referências ocorrem antes da regra"""
        result = True
        
        # Verifica cada referência disponível
        for i in range(1, 6):
            ref_attr = f'reference{i}'
            if hasattr(rule_def, ref_attr):
                ref = getattr(rule_def, ref_attr)
                if ref and int(ref.value) >= int(rule_def.line):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.REFERENCED_LINE_NOT_DEFINED, ref, rule_def)
                    )
                    result = False
                    
        return result
    
    def _check_line_scope_reference_error(self, rule_def):
        """Verifica se as referências estão no escopo da regra"""
        # Verifica cada referência disponível
        for i in range(1, 6):
            ref_attr = f'reference{i}'
            if hasattr(rule_def, ref_attr):
                ref = getattr(rule_def, ref_attr)
                if ref and (self.parser.symbol_table.lookup_formula_by_line(rule_def.line, ref.value) is None):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.USING_DESCARTED_RULE, ref, rule_def)
                    )
    
    def _needs_scope_validation(self, rule_def):
        """Determina se a regra precisa de validação de escopo"""
        rule_types_needing_scope = [
            'IMP_INTRO', 'NEG_INTRO', 'RAA', 'ALL_INTRO', 'EXT_ELIM'
        ]
        return rule_def.rule_type in rule_types_needing_scope
    
    def _check_scope_reference_error(self, rule_def):
        """Validações complexas de escopo para regras com caixas"""
        result = True
        
        if rule_def.rule_type in ['IMP_INTRO', 'NEG_INTRO', 'RAA', 'ALL_INTRO']:
            # Regras com 2 referências que formam uma caixa
            if len(rule_def.references) >= 2:
                ref1, ref2 = rule_def.references[0], rule_def.references[1]
                formula1, formula2 = self.parser.symbol_table.check_scope_delimiter(ref1.value, ref2.value)
                
                # Verifica se forma uma caixa válida
                if formula1 is None:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref1, rule_def)
                    )
                    result = False
                
                # Verifica sequência temporal
                elif not (int(rule_def.line) > int(ref2.value) and int(ref2.value) >= int(ref1.value)):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref1, rule_def)
                    )
                    result = False
                
                # Verifica fechamento imediato
                if int(rule_def.line) != int(ref2.value) + 1 and not getattr(rule_def, 'is_copied', False):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, ref1, rule_def)
                    )
                    result = False
        
        elif rule_def.rule_type == 'EXT_ELIM':
            # Eliminação do existencial com 3 referências
            if len(rule_def.references) >= 3:
                ref1, ref2, ref3 = rule_def.references[0], rule_def.references[1], rule_def.references[2]
                formula1, formula2 = self.parser.symbol_table.check_scope_delimiter(ref2.value, ref3.value)
                
                # Validações específicas para eliminação do existencial
                if formula1 is None:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref2, rule_def)
                    )
                    result = False
                
                # Verifica sequência temporal
                elif not (int(rule_def.line) > int(ref3.value) and 
                         int(ref3.value) >= int(ref2.value) and 
                         int(ref2.value) >= int(ref1.value)):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref2, rule_def)
                    )
                    result = False
                
                # Verifica fechamento imediato
                if int(rule_def.line) != int(ref3.value) + 1:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, ref2, rule_def)
                    )
                    result = False
                
                # Validações específicas de variável fresca
                variable = self.parser.symbol_table.find_scope_variable(ref2.value)
                if variable is None:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.BOX_MUST_HAVE_A_VARIABLE, ref2, rule_def)
                    )
                    result = False
                elif not self.parser.symbol_table.is_fresh_variable(ref2.value):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.VARIABLE_IS_NOT_FRESH_VARIABLE, ref2, rule_def)
                    )
                    result = False
        
        elif rule_def.rule_type == 'OR_ELIM':
            # Eliminação da disjunção com 5 referências
            if len(rule_def.references) >= 5:
                ref1, ref2, ref3, ref4, ref5 = rule_def.references
                
                # Valida primeira caixa
                formula1, formula2 = self.parser.symbol_table.check_scope_delimiter(ref2.value, ref3.value)
                if formula1 is None:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref2, rule_def)
                    )
                    result = False
                
                # Valida segunda caixa
                formula3, formula4 = self.parser.symbol_table.check_scope_delimiter(ref4.value, ref5.value)
                if formula3 is None:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref4, rule_def)
                    )
                    result = False
                
                # Verifica sequência temporal complexa
                if not (int(rule_def.line) > int(ref5.value) and 
                       int(ref5.value) >= int(ref4.value) and 
                       int(ref4.value) == int(ref3.value) + 1 and
                       int(ref3.value) >= int(ref2.value) and
                       int(ref2.value) >= int(ref1.value)):
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.INVALID_SCOPE_DELIMITER, ref2, rule_def)
                    )
                    result = False
                
                # Verifica fechamento imediato
                if int(rule_def.line) != int(ref5.value) + 1:
                    self.parser.has_error = True
                    self.deduction_result.add_error(
                        self.parser.get_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE, ref4, rule_def)
                    )
                    result = False
        
        return result
    
    def validate_copy_rule(self, rule_def, original_line):
        """Validação específica para regra de cópia"""
        copied_scope = self.parser.symbol_table.find_scope(original_line)
        if not self.parser.symbol_table.check_scope_is_valid(copied_scope):
            self.parser.has_error = True
            self.deduction_result.add_error(
                self.parser.get_error(constants.USING_DESCARTED_RULE, rule_def.references[0], None)
            )
            return False
        
        # Verifica se a fórmula copiada é igual à original
        original_formula = self.parser.symbol_table.lookup_formula_by_line(rule_def.line, original_line)
        if original_formula != rule_def.formula:
            self.parser.has_error = True
            self.deduction_result.add_error(
                self.parser.get_error(constants.COPY_DIFFERENT_FORMULE, rule_def.references[0], rule_def)
            )
            return False
            
        return True
    
    def validate_hypothesis(self, rule_def, formula_token):
        """Validação para hipóteses"""
        if self.parser.symbol_table.current_scope == "scope_0":
            self.parser.has_error = True
            self.deduction_result.add_error(
                self.parser.get_error(constants.HYPOTHESIS_WITHOUT_BOX, formula_token, rule_def)
            )
            return False
        return True
    
    def validate_wrong_rules(self, rule_def, error_token, error_type):
        """Validação para regras incorretas"""
        self.parser.has_error = True
        self.deduction_result.add_error(
            self.parser.get_error(error_type, error_token, rule_def)
        )
        return False