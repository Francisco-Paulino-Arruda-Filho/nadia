class natural_deduction_return:
    def __init__(self):
        self.premisses = []
        self.conclusion = None
        self.gentzen = ""
        self.fitch = ""
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)