from Strategy.ParserValidator import ParserValidator
from Strategy.RuleContext import RuleContext


class RuleDefinition:
    def evaluation(self, parser, deduction_result):
        if not self._strategy:
            deduction_result.add_error(f"Tipo de regra desconhecido: {self.rule_type}")
            return

        # ✅ USAR ParserValidator COMPLETO
        validator = ParserValidator(parser, deduction_result)
        
        # Validações estruturais completas
        if not validator.validate_references(self):
            return  # Se falhar nas validações estruturais, não prossegue

        # Validação semântica específica da regra usando Strategy
        context = RuleContext(
            symbol_table=parser.symbol_table,
            line=self.line,
            formula=self.formula,
            references=self.references,
            hypothesis=getattr(parser, "hypothesis", {})
        )

        if not self._strategy.validate(context):
            for error in context.errors:
                error_type = self._map_error_type(error)
                error_token = self.references[0] if self.references else None
                deduction_result.add_error(
                    parser.get_error(error_type, error_token, self)
                )