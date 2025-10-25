from ParserFactory.ParserNadia import ParserNadia
from ParserFactory.ParserTheorem import ParserTheorem
from ParserFactory.ParserFormula import ParserFormula
from ParserInterface import ParserInterface
from ParserType import ParserType

class ParserFactory:
    """Fábrica para criar diferentes tipos de parsers"""
    
    @staticmethod
    def create_parser(parser_type: ParserType, input_text: str) -> ParserInterface:
        """
        Cria um parser baseado no tipo especificado
        
        Args:
            parser_type: Tipo do parser (THEOREM, FORMULA, PROOF)
            input_text: Texto de entrada para o parser
            
        Returns:
            Instância do parser específico
        """
        if parser_type == ParserType.THEOREM:
            return ParserTheorem(input_text)
        elif parser_type == ParserType.FORMULA:
            return ParserFormula(input_text)
        elif parser_type == ParserType.NADIA:
            return ParserNadia(input_text)
        else:
            raise ValueError(f"Tipo de parser não suportado: {parser_type}")
    
    @staticmethod
    def create_parser_by_content(input_text: str) -> ParserInterface:
        """
        Cria o parser automaticamente baseado no conteúdo do texto
        """
        input_text_lower = input_text.lower().strip()
        
        # Heurística para detectar o tipo
        if "|-" in input_text or "⊢" in input_text:
            return ParserFactory.create_parser(ParserType.THEOREM, input_text)
        elif any(word in input_text_lower for word in ['pre', 'hip', 'imp_elim', 'imp_introd']):
            return ParserFactory.create_parser(ParserType.PROOF, input_text)
        else:
            # Assume que é uma fórmula simples
            return ParserFactory.create_parser(ParserType.FORMULA, input_text)