from Strategy.InferenceRuleFactory import InferenceRuleFactory
from Strategy.InferenceContext import InferenceContext

class RuleDefinition:
    """Classe unificada que substitui todas as classes *Def específicas"""
    
    def __init__(self, line, formula, rule_type, references):
        self.line = line
        self.formula = formula
        self.rule_type = rule_type
        self.references = references
        self.is_copied = False
        self._strategy = InferenceRuleFactory.create_rule(rule_type)
    
    def evaluation(self, parser, deduction_result):
        """Executa a validação usando a estratégia"""
        if not self._strategy:
            deduction_result.add_error(f"Tipo de regra desconhecido: {self.rule_type}")
            return
        
        # Valida referências básicas
        if not parser.check_line_reference_before_rule_error(deduction_result, self):
            return
        
        # Valida escopo das referências
        parser.check_line_scope_reference_error(deduction_result, self, 
                                              reference1=len(self.references) > 0,
                                              reference2=len(self.references) > 1)
        
        # Valida escopo para regras de caixa
        if self.rule_type in ['IMP_INTROD']:
            parser.check_scope_reference_error(deduction_result, self)
        
        # Cria contexto e aplica validação específica da regra
        context = InferenceContext(
            symbol_table=parser.symbol_table,
            line=self.line,
            formula=self.formula,
            references=self.references,
            hypothesis=hypothesis  # usa a variável global hypothesis
        )
        
        if not self._strategy.validate(context):
            for error in context.errors:
                # Usa o primeiro token de referência para reportar erro, se disponível
                error_token = self.references[0] if self.references else None
                deduction_result.add_error(parser.get_error("INVALID_RULE", error_token, self))
    
    def toLatex(self, symbol_table):
        """Gera notação LaTeX usando a estratégia"""
        if not self._strategy:
            return f"{{{self.formula.toLatex()}}}"
        
        context = InferenceContext(
            symbol_table=symbol_table,
            line=self.line,
            formula=self.formula,
            references=self.references,
            hypothesis=hypothesis  # usa a variável global hypothesis
        )
        
        return self._strategy.get_latex_notation(context)