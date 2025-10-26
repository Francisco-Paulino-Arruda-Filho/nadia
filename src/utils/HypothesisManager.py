from typing import Dict


class HypothesisManager:
    _instance = None
    _hypothesis = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HypothesisManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_hypothesis_number(cls, line: str) -> str:
        if line not in cls._hypothesis:
            cls._hypothesis[line] = str(len(cls._hypothesis) + 1)
        return cls._hypothesis[line]
    
    @classmethod
    def reset(cls):
        cls._hypothesis = {}
    
    @classmethod
    def get_all_hypotheses(cls) -> Dict:
        return cls._hypothesis.copy()