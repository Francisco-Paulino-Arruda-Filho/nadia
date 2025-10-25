from Strategy.ImplicationEliminationDef import ImplicationEliminationDef
from Strategy.ImplicationIntroductionDef import ImplicationIntroductionDef

class InferenceRuleFactory:
    """Fábrica para criar regras de inferência baseadas no tipo"""
    
    _rules = {
        'IMP_ELIM': ImplicationEliminationDef,
        'IMP_INTROD': ImplicationIntroductionDef,
        # Adicione outras regras aqui conforme necessário
    }
    
    @classmethod
    def create_rule(cls, rule_type: str):
        """Cria uma instância da regra baseada no tipo"""
        rule_class = cls._rules.get(rule_type)
        return rule_class() if rule_class else None
    
    @classmethod
    def register_rule(cls, rule_type: str, rule_class):
        """Permite registrar novas regras dinamicamente"""
        cls._rules[rule_type] = rule_class