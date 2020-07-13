class LLException(Exception):
   def __init__(self, errCode, msgPrefix, msg):
        super().__init__(f"{errCode} {msgPrefix}: {msg}")
        self.msg = f"{errCode} {msgPrefix}: {msg}"
        self.errCode = errCode

class LexicalException(LLException):
    def __init__(self, line, msg):
        super().__init__(10, f"L{line} Lexical Error", msg)

class GrammarNotLL1Exception(LLException):
    def __init__(self, nonterminal, terminal, rule1, rule2):
        super().__init__(20, f"Provided grammar is not an LL(1) grammar", f'Both "{rule1}" and "{rule2}" can derive "{nonterminal}/{terminal}"')