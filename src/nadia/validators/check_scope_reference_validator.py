from abc import ABC, abstractmethod

from models.constants import constants

class BaseScopeChecker(ABC):
    def __init__(self, context):
        self.context = context
        self.result = True

    def _add_error(self, error_code, reference, rule, deduction_result):
        """Helper interno para padronizar o relatório de erros."""
        self.context.has_error = True
        self.result = False
        error = self.context.get_error(error_code, reference, rule)
        deduction_result.add_error(error)

    @abstractmethod
    def get_scope_boxes(self, rule):
        pass

    @abstractmethod
    def validate_box_order(self, rule, start_ref, end_ref):
        pass

    def validate_box_closing(self, rule, deduction_result):
        return True

    # --- O "Template Method" ---

    def check(self, rule, deduction_result):
        """
        Este é o Template Method. Ele define a ordem da execução
        e não deve ser sobrescrito.
        """
        self.result = True

        # 1. Obter as "boxes" de escopo da subclasse
        boxes_to_check = self.get_scope_boxes(rule)

        # 2. Iterar e checar cada box (lógica comum)
        for (start_ref, end_ref, error_ref) in boxes_to_check:

            # 2a. Checagem de delimitador de escopo (comum a todos)
            formula1, _ = self.context.symbol_table.check_scope_delimiter(
                start_ref.value, end_ref.value
            )
            if formula1 is None:
                self._add_error(constants.INVALID_SCOPE_DELIMITER,
                                error_ref, rule, deduction_result)
                # Se este box é inválido, pular para o próximo
                continue

            # 2b. Checagem da ordem (delegado à subclasse)
            if not self.validate_box_order(rule, start_ref, end_ref):
                self._add_error(constants.INVALID_SCOPE_DELIMITER,
                                error_ref, rule, deduction_result)

        # 3. Checagem final de fechamento (delegado ao hook)
        # Só executa se as checagens de box passaram
        if self.result:
            self.validate_box_closing(rule, deduction_result)

        return self.result


class StandardScopeChecker(BaseScopeChecker):
    """Verificador para a maioria das regras de introdução que abrem um escopo."""

    def get_scope_boxes(self, rule):
        return [(rule.reference1, rule.reference2, rule.reference1)]

    def validate_box_order(self, rule, start_ref, end_ref):
        return (int(rule.line) > int(end_ref.value) and
                int(end_ref.value) >= int(start_ref.value))

    def validate_box_closing(self, rule, deduction_result):
        if int(rule.line) != int(rule.reference2.value) + 1 and not rule.is_copied:
            self._add_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE,
                            rule.reference1, rule, deduction_result)
            return False
        return True


class ExistsEliminationScopeChecker(BaseScopeChecker):
    """Verificador específico para ExistsEliminationDef."""

    def get_scope_boxes(self, rule):
        return [(rule.reference2, rule.reference3, rule.reference2)]

    def validate_box_order(self, rule, start_ref, end_ref):
        return (int(rule.line) > int(end_ref.value) and
                int(end_ref.value) >= int(start_ref.value) and
                int(start_ref.value) >= int(rule.reference1.value))

    def validate_box_closing(self, rule, deduction_result):
        if int(rule.line) != int(rule.reference3.value) + 1:
            self._add_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE,
                            rule.reference2, rule, deduction_result)
            return False
        return True


class DisjunctionEliminationScopeChecker(BaseScopeChecker):
    """Verificador para DisjunctionEliminationDef, que checa dois boxes."""

    def get_scope_boxes(self, rule):
        box1 = (rule.reference2, rule.reference3, rule.reference2)
        box2 = (rule.reference4, rule.reference5, rule.reference4)
        return [box1, box2]

    def validate_box_order(self, rule, start_ref, end_ref):
        if start_ref == rule.reference2:
            return (int(rule.line) > int(end_ref.value) and
                    int(end_ref.value) >= int(start_ref.value) and
                    int(start_ref.value) >= int(rule.reference1.value))

        elif start_ref == rule.reference4:
            return (int(rule.line) > int(end_ref.value) and
                    int(end_ref.value) >= int(start_ref.value) and
                    int(start_ref.value) == int(rule.reference3.value) + 1)

        return False  

    def validate_box_closing(self, rule, deduction_result):
        if int(rule.line) != int(rule.reference5.value) + 1:
            self._add_error(constants.BOX_MUST_BE_DISPOSED_BY_RULE,
                            rule.reference4, rule, deduction_result)
            return False
        return True