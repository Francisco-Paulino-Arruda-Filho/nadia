from models.constants import constants
from nadia.validators.base_scope_checker import BaseScopeChecker


class DisjunctionEliminationScopeChecker(BaseScopeChecker):
    """Verificador para DisjunctionEliminationDef, que checa dois  boxes."""

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
