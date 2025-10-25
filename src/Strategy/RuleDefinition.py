from Strategy.InferenceContext import InferenceContext
from Strategy.InferenceRuleFactory import InferenceRuleFactory
from models import constants


class RuleDefinition:
    """Classe unificada que substitui todas as classes *Def específicas"""

    def __init__(self, line, formula, rule_type, references):
        self.line = line
        self.formula = formula
        self.rule_type = rule_type
        self.references = references
        self.is_copied = False
        self._strategy = InferenceRuleFactory.create_rule(rule_type)

    # -------------------------------------------------------------
    # Avaliação da regra de inferência
    # -------------------------------------------------------------
    def evaluation(self, parser, deduction_result):
        """Executa a validação usando a estratégia (mantendo comportamento original)"""
        if not self._strategy:
            deduction_result.add_error(f"Tipo de regra desconhecido: {self.rule_type}")
            return

        # 1️⃣ Verifica se as referências ocorrem antes da linha da regra
        before_ok = parser.check_line_reference_before_rule_error(deduction_result, self)
        if not before_ok:
            return  # Se falhar, não prossegue — igual ao original

        # 2️⃣ Verifica se as referências estão no mesmo escopo
        parser.check_line_scope_reference_error(
            deduction_result,
            self,
            reference1=len(self.references) > 0,
            reference2=len(self.references) > 1
        )

        # 3️⃣ Verifica delimitadores de escopo apenas para regras que usam caixas
        if self.rule_type in ['IMP_INTROD']:
            parser.check_scope_reference_error(deduction_result, self)

        # 4️⃣ Recupera a fórmula da linha (equivalente ao find_token do original)
        formula_reference = parser.symbol_table.find_token(self.line)
        if formula_reference is None:
            deduction_result.add_error(parser.get_error(constants.INVALID_RESULT, None, self))
            return

        # 5️⃣ Cria o contexto de inferência
        context = InferenceContext(
            symbol_table=parser.symbol_table,
            line=self.line,
            formula=self.formula,
            references=self.references,
            hypothesis=getattr(parser, "hypothesis", {})  # fallback seguro
        )

        # 6️⃣ Executa a validação específica da regra via Strategy
        if not self._strategy.validate(context):
            for error in context.errors:
                # Mapear mensagem humana para tipo de erro compatível
                error_type = self._map_error_type(error)
                error_token = self.references[0] if self.references else None
                deduction_result.add_error(
                    parser.get_error(error_type, error_token, self)
                )

    # -------------------------------------------------------------
    # Geração da notação LaTeX
    # -------------------------------------------------------------
    def toLatex(self, symbol_table, hypothesis):
        """Gera notação LaTeX usando a estratégia"""
        if not self._strategy:
            return f"{{{self.formula.toLatex()}}}"

        context = InferenceContext(
            symbol_table=symbol_table,
            line=self.line,
            formula=self.formula,
            references=self.references,
            hypothesis=hypothesis or {}  # garante dicionário válido
        )

        return self._strategy.get_latex_notation(context)

    # -------------------------------------------------------------
    # Utilitário interno para mapear mensagens para constantes
    # -------------------------------------------------------------
    def _map_error_type(self, message: str) -> str:
        """Mapeia mensagens textuais do Strategy para tipos de erro do parser"""
        message = message.lower()
        if "hipótese" in message:
            return constants.INVALID_HYPOTHESIS
        elif "caixa" in message or "conclusão" in message:
            return constants.INVALID_BOX_RESULT
        elif "implicação" in message or "combinação" in message:
            return constants.INVALID_RESULT
        else:
            return constants.INVALID_RULE
