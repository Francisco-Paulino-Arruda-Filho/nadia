import traceback
import sys

from nadia.parser.natural_deduction_return import natural_deduction_return
from nadia.parser.parser_nadia import ParserNadia
from nadia.parser.parser_theorem import ParserTheorem


deduction_result = natural_deduction_return()


def value_error_handle(exctype, value, tb):
    deduction_result.add_error(str(value))


sys.excepthook = value_error_handle

def check_proof(input_proof, input_theorem=None, display_theorem=True, display_fitch=True, display_gentzen=True):
    try:
        result = ParserNadia.getProof(input_proof)
        r = ''

        if(result.errors==[]):
            s_theorem = ParserNadia.toString(result.premisses, result.conclusion)
            if input_theorem is not None: 
                premisses, conclusion = ParserTheorem.getTheorem(input_theorem)
                if conclusion is None:
                    return f'{input_theorem} não é um teorema válido!'

                set_premisses = set([p.toString() for p in premisses])
                set_premisses_result = set([p.toString() for p in result.premisses])
                if(conclusion==result.conclusion and set_premisses==set_premisses_result):
                    r += "A demonstração está correta."
                    if display_theorem:
                       r += "\n"+s_theorem
                else:
                    r += f"Sua demostração de {s_theorem} é válida, mas é diferente da demonstração solicitada {input_theorem}"
            else:
                r += "A demonstração está correta."
                if display_theorem:
                    r += "\n"+s_theorem
            if display_fitch:
                r += "\n\nCódigo da demonstração no estilo Fitch em Latex:\n"
                r += str(result.fitch)
            if display_gentzen:
                r += "\n\nCódigo da demonstração no estilo Gentzen em Latex:\n"
                r += str(result.gentzen)
        else:
            r += "Os seguintes erros foram encontrados:\n\n"
            for error in result.errors:
                r += str(error)
        return r
    except ValueError:
        s = traceback.format_exc()
        result = (s.split("@@"))[-1]
        r = "Os seguintes erros foram encontrados:\n\n"
        r += result
        return r
    else:
        pass

