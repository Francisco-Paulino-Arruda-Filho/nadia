from models.constants import constants
from nadia.validators.base_scope_checker import BaseScopeChecker


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
