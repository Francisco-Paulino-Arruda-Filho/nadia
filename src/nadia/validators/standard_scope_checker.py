from models.constants import constants
from nadia.validators.base_scope_checker import BaseScopeChecker


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
