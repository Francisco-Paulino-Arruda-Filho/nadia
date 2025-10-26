from Factory.RuleBase import RuleBase

class RuleFactory:
    """Factory para criação de regras de inferência"""
    
    @staticmethod
    def create_rule(rule_type: str, line: str, formula, *references) -> RuleBase:
        # Import dentro do método para evitar circular imports
        from Factory.PremisseDef import PremisseDef
        from Factory.HypothesisDef import HypothesisDef
        from Factory.HypothesisFirstOrderDef import HypothesisFirstOrderDef
        from Factory.ImplicationEliminationDef import ImplicationEliminationDef
        from Factory.ImplicationIntroductionDef import ImplicationIntroductionDef
        from Factory.AndIntroductionDef import AndIntroductionDef
        from Factory.AndEliminationDef import AndEliminationDef
        from Factory.DisjunctionIntroductionDef import DisjunctionIntroductionDef
        from Factory.DisjunctionEliminationDef import DisjunctionEliminationDef
        from Factory.NegationIntroductionDef import NegationIntroductionDef
        from Factory.NegationEliminationDef import NegationEliminationDef
        from Factory.BottomDef import BottomDef
        from Factory.RaaDef import RaaDef
        from Factory.CopyDef import CopyDef
        from Factory.ForAllEliminationDef import ForAllEliminationDef
        from Factory.ExistsIntroductionDef import ExistsIntroductionDef
        from Factory.ExistsEliminationDef import ExistsEliminationDef
        from Factory.ForAllIntroductionDef import ForAllIntroductionDef
        from Factory.WrongDef import WrongDef

        rule_creators = {
            'premise': lambda: PremisseDef(line, formula),
            'hypothesis': lambda: HypothesisDef(line, formula),
            'hypothesis_first_order': lambda: HypothesisFirstOrderDef(line, references[0] if references else None, formula),
            'implication_elimination': lambda: ImplicationEliminationDef(line, formula, references[0], references[1]),
            'implication_introduction': lambda: ImplicationIntroductionDef(line, formula, references[0], references[1]),
            'and_introduction': lambda: AndIntroductionDef(line, formula, references[0], references[1]),
            'and_elimination': lambda: AndEliminationDef(line, formula, references[0]),
            'disjunction_introduction': lambda: DisjunctionIntroductionDef(line, formula, references[0]),
            'disjunction_elimination': lambda: DisjunctionEliminationDef(line, formula, references[0], references[1], references[2], references[3], references[4]),
            'negation_introduction': lambda: NegationIntroductionDef(line, formula, references[0], references[1]),
            'negation_elimination': lambda: NegationEliminationDef(line, formula, references[0], references[1]),
            'bottom_elimination': lambda: BottomDef(line, formula, references[0]),
            'raa': lambda: RaaDef(line, formula, references[0], references[1]),
            'copy': lambda: CopyDef(line, formula, references[0]),
            'forall_elimination': lambda: ForAllEliminationDef(line, formula, references[0]),
            'exists_introduction': lambda: ExistsIntroductionDef(line, formula, references[0]),
            'exists_elimination': lambda: ExistsEliminationDef(line, formula, references[0], references[1], references[2]),
            'forall_introduction': lambda: ForAllIntroductionDef(line, formula, references[0], references[1]),
            'wrong': lambda: WrongDef(line, formula),
        }
        
        if rule_type not in rule_creators:
            return WrongDef(line, formula)
        
        return rule_creators[rule_type]()