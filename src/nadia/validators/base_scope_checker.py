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

        # 2. Iterar e checar cada box 
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