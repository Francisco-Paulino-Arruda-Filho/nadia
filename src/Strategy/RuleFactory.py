from Strategy.AndEliminationDef import AndEliminationDef
from Strategy.AndIntroductionDef import AndIntroductionDef
from Strategy.PremisseDef import PremisseDef
from Strategy.BottomDef import BottomDef
from Strategy.DisjunctionIntroductionDef import DisjunctionIntroductionDef
from Strategy.RaaDef import RaaDef
from Strategy.DisjunctionEliminationDef import DisjunctionEliminationDef
from Strategy.DisjunctionIntroductionDef import DisjunctionIntroductionDef
from Strategy.ImplicationEliminationDef import ImplicationEliminationDef
from Strategy.ImplicationIntroductionDef import ImplicationIntroductionDef
from Strategy.NegationEliminationDef import NegationEliminationDef
from Strategy.NegationIntroductionDef import NegationIntroductionDef

from Strategy.ExistsEliminationDef import ExistsEliminationDef
from Strategy.ExistsIntroductionDef import ExistsIntroductionDef
from Strategy.ForAllEliminationDef import ForAllEliminationDef
from Strategy.ForAllIntroductionDef import ForAllIntroductionDef

from Strategy.HypothesisDef import HypothesisDef
from Strategy.HypothesisFirstOrderDef import HypothesisFirstOrderDef
from Strategy.CopyDef import CopyDef
from Strategy.WrongDef import WrongDef

class RuleFactory:
    """Fábrica para criar regras de inferência baseadas no tipo"""
    
    _rules = {
        # Regras proposicionais básicas
        'PREMISE': PremisseDef,
        'HYPOTHESIS': HypothesisDef,
        'HYPOTHESIS_FO': HypothesisFirstOrderDef,

        # Conectivos lógicos
        'AND_INTRO': AndIntroductionDef,
        'AND_ELIM': AndEliminationDef,
        'OR_INTRO': DisjunctionIntroductionDef,
        'OR_ELIM': DisjunctionEliminationDef,
        'IMP_INTRO': ImplicationIntroductionDef,
        'IMP_ELIM': ImplicationEliminationDef,
        'NEG_INTRO': NegationIntroductionDef,
        'NEG_ELIM': NegationEliminationDef,
        'BOTTOM': BottomDef,
        'RAA': RaaDef,
        'COPY': CopyDef,
        'WRONG': WrongDef,

        # Quantificadores (lógica de primeira ordem)
        'FORALL_INTRO': ForAllIntroductionDef,
        'FORALL_ELIM': ForAllEliminationDef,
        'EXISTS_INTRO': ExistsIntroductionDef,
        'EXISTS_ELIM': ExistsEliminationDef,
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