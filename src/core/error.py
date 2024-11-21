class CustomError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__()
