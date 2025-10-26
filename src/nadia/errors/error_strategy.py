from abc import ABC, abstractmethod
from models.constants import constants


class ErrorStrategy(ABC):
    """Classe abstrata base para estratégias de erro."""

    @abstractmethod
    def format_error(self, productions, token_error, rule) -> str:
        pass

    def _build_header(self, productions, token_error):
        """Constrói o cabeçalho padrão do erro."""
        column_error = token_error.getsourcepos().colno
        erro = f"Erro de sintaxe na linha {token_error.getsourcepos().lineno}:\n"
        erro += productions[token_error.getsourcepos().lineno - 1] + "\n"
        erro += " " * (column_error - 1)
        return erro


class ReferencedFormulaNoneError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula {token_error.value} não foi definida anteriormente ou foi descartada.\n"
        return erro


class InvalidResultError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula {rule.formula.toString()} não é um resultado válido para esta regra."
        return erro


class InvalidHypothesisError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A hipótese da linha {token_error.value} não corresponde a hipótese esperada para a fórmula da conclusão desta regra."
        return erro


class InvalidBoxResultError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula da linha {token_error.value} não corresponde a conclusão esperada desta caixa para esta regra."
        return erro


class UnexpectedResultError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula {rule.formula.toString()} não é um resultado válido para a regra aplicada."
        return erro


class IsNotDisjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += (
            f"^, A fórmula referenciada na linha {token_error.value} não é disjunção."
        )
        return erro


class IsNotConjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += (
            f"^, A fórmula referenciada na linha {token_error.value} não é conjunção."
        )
        return erro


class IsNotImplicationError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += (
            f"^, A fórmula referenciada na linha {token_error.value} não é implicação."
        )
        return erro


class IsNotBottomError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula referenciada na linha {token_error.value} deveria ser @."
        return erro


class InvalidNegationError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, Nenhuma das fórmulas referencias pelas linhas é a negação da outra fórmula."
        return erro


class InvalidLeftConjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A fórmula à esquerda fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        return erro


class InvalidRightConjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A fórmula à direita da fórmula da conclusão não é demonstrada por nenhuma das linhas referenciadas nesta regra."
        return erro


class InvalidLeftOrRightDisjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula à direita ou à equerda da fórmula da conclusão deve ser a mesma da fórmula referencia na linha {token_error.value}."
        return erro


class InvalidLeftOrRightConjunctionError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula à direita ou à equerda da fórmula da linha {token_error.value} deve ser a mesma da fórmula da conclusão da regra."
        return erro


class NoneCopyError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A Fórmula referenciada para cópia não existe."
        return erro


class CopyDifferentFormuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A Fórmula referenciada para cópia é diferente da definida para essa regra."
        return erro


class InvalidHipPreWriteError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, uma hipótese só pode ser usado no início de uma caixa e é introduzida apenas por uma regra de inferência."
        return erro


class InvalidRuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, a regra {token_error.value} deve ter duas referências separadas por vírgula."
        return erro


class InvalidRuleOneReferenceError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, a regra {token_error.value} deve ter uma única referência."
        return erro


class ExcedentHipPreWriteError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, Não é esperado texto depois de pre."
        return erro


class UsingDescartedRuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, a referência a fórmula da linha {token_error.value} não pode ser utilizada, pois esta fórmula já foi descartada."
        return erro


class ReferencedLineNotDefinedError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, a referência a fórmula da linha {token_error.value} não pode ser utilizada, pois todas as referências devem ocorrer antes desta regra."
        return erro


class InvalidScopeDelimiterError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, esta não é uma caixa (escopo) válida."
        return erro


class HypothesisWithoutBoxError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A hipótese definida não está dentro de uma caixa."
        return erro


class CloseBracketWithoutBoxError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, Fechamento de caixa sem caixa aberta."
        return erro


class HypothesisWithoutClosedBoxError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, É necessário fechar o escopo desta caixa."
        return erro


class BoxMustBeDisposedError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A hipótese que foi introduzida por essa caixa dever ser descartada pela regra que a introduziu em linha imediatamente posterior ao fechamento desta caixa."
        return erro


class BoxMustBeDisposedByRuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, Esta caixa dever ser fechada em linha imediatamente posterior pela regra que a introduziu."
        return erro


class InvalidSubstitutionUniversalError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula {rule.formula.toString()} não é uma substituição válida da fórmula universal refenciada na linha {rule.reference1.value}."
        return erro


class InvalidConclusionExistentialLastRuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A formula da conclusão desta regra deve ser a mesma fórmula refenciada na linha {token_error.value}."
        return erro


class InvalidConclusionUniversalLastRuleError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A formula da conclusão desta regra deve ser a quantificação universal da fórmula refenciada na linha {token_error.value} com a variável definida neste escopo."
        return erro


class InvalidUniversalFormulaError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += "^, A fórmula referenciada na regra do universal não é uma fórmula do tipo universal."
        return erro


class InvalidSubstitutionExistentialError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A fórmula {rule.formula.toString()} não é uma substituição válida da fórmula existencial refenciada na linha {rule.reference1.value}."
        return erro


class VariableIsNotFreshVariableError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A variável utilizada na linha {token_error.value} é uma variável livre de uma fórmula definida anteriormente e, portanto, não pode ser utilizada nesta regra."
        return erro


class BoxMustHaveAVariableError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A caixa que inicia na linha {token_error.value} deve iniciar com uma variável para esta regra."
        return erro


class BoxMustHaveOnlyAVariableError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A caixa que inicia na linha {token_error.value} não tem hipótese. A caixa deve iniciar com uma variável apenas para a regra da introdução do universal."
        return erro


class InvalidConclusionExistentialError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A variável utilizada na conclusão dessa regra não pode ser a variável utilizada na caixa que inicia na linha {token_error.value}."
        return erro


class InvalidConclusionUniversalError(ErrorStrategy):
    def format_error(self, productions, token_error, rule):
        erro = self._build_header(productions, token_error)
        erro += f"^, A variável utilizada na caixa que inicia na linha {token_error.value} não pode ocorrer como variável livre na conclusão da fórmula e, portanto, não pode ser utilizada nesta regra."
        return erro


class ErrorContext:
    """Contexto para gerenciar estratégias de erro."""

    def __init__(self):
        """Inicializa o contexto com todas as estratégias mapeadas."""
        self.strategies = {
            constants.REFERENCED_FORMULE_NONE: ReferencedFormulaNoneError(),
            constants.INVALID_RESULT: InvalidResultError(),
            constants.INVALID_HYPOTHESIS: InvalidHypothesisError(),
            constants.INVALID_BOX_RESULT: InvalidBoxResultError(),
            constants.UNEXPECT_RESULT: UnexpectedResultError(),
            constants.IS_NOT_DISJUNCTION: IsNotDisjunctionError(),
            constants.IS_NOT_CONJUNCTION: IsNotConjunctionError(),
            constants.IS_NOT_IMPLICATION: IsNotImplicationError(),
            constants.IS_NOT_BOTTOM: IsNotBottomError(),
            constants.INVALID_NEGATION: InvalidNegationError(),
            constants.INVALID_LEFT_CONJUNCTION: InvalidLeftConjunctionError(),
            constants.INVALID_RIGHT_CONJUNCTION: InvalidRightConjunctionError(),
            constants.INVALID_LEFT_OR_RIGHT_DISJUNCTION: InvalidLeftOrRightDisjunctionError(),
            constants.INVALID_LEFT_OR_RIGHT_CONJUNCTION: InvalidLeftOrRightConjunctionError(),
            constants.NONE_COPY: NoneCopyError(),
            constants.COPY_DIFFERENT_FORMULE: CopyDifferentFormuleError(),
            constants.INVALID_HIP_PRE_WRITE: InvalidHipPreWriteError(),
            constants.INVALID_RULE: InvalidRuleError(),
            constants.INVALID_RULE_ONE_REFERENCE: InvalidRuleOneReferenceError(),
            constants.EXCEDENT_HIP_PRE_WRITE: ExcedentHipPreWriteError(),
            constants.USING_DESCARTED_RULE: UsingDescartedRuleError(),
            constants.REFERENCED_LINE_NOT_DEFINED: ReferencedLineNotDefinedError(),
            constants.INVALID_SCOPE_DELIMITER: InvalidScopeDelimiterError(),
            constants.HYPOTHESIS_WITHOUT_BOX: HypothesisWithoutBoxError(),
            constants.CLOSE_BRACKET_WITHOUT_BOX: CloseBracketWithoutBoxError(),
            constants.HYPOTHESIS_WITHOUT_CLOSED_BOX: HypothesisWithoutClosedBoxError(),
            constants.BOX_MUST_BE_DISPOSED: BoxMustBeDisposedError(),
            constants.BOX_MUST_BE_DISPOSED_BY_RULE: BoxMustBeDisposedByRuleError(),
            constants.INVALID_SUBSTITUTION_UNIVERSAL: InvalidSubstitutionUniversalError(),
            constants.INVALID_CONCLUSION_EXISTENTIAL_LAST_RULE: InvalidConclusionExistentialLastRuleError(),
            constants.INVALID_CONCLUSION_UNIVERSAL_LAST_RULE: InvalidConclusionUniversalLastRuleError(),
            constants.INVALID_UNIVERSAL_FORMULA: InvalidUniversalFormulaError(),
            constants.INVALID_SUBSTITUTION_EXISTENTIAL: InvalidSubstitutionExistentialError(),
            constants.VARIABLE_IS_NOT_FRESH_VARIABLE: VariableIsNotFreshVariableError(),
            constants.BOX_MUST_HAVE_A_VARIABLE: BoxMustHaveAVariableError(),
            constants.BOX_MUST_HAVE_ONLY_A_VARIABLE: BoxMustHaveOnlyAVariableError(),
            constants.INVALID_CONCLUSION_EXISTENTIAL: InvalidConclusionExistentialError(),
            constants.INVALID_CONCLUSION_UNIVERSAL: InvalidConclusionUniversalError(),
        }

    def get_error(self, state, type_error, token_error, rule) -> str:
        productions = state.splitlines()
        strategy = self.strategies.get(type_error)

        if strategy:
            return strategy.format_error(productions, token_error, rule)

        # Fallback para erro desconhecido
        return f"Erro desconhecido: tipo {type_error}"
