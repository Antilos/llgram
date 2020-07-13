class LLException(Exception):
   def __init__(self, errCode, msgPrefix, msg):
        super().__init__(f"{errCode} {msgPrefix}: {msg}")
        self.msg = f"{errCode} {msgPrefix}: {msg}"
        self.errCode = errCode

class GrammarException(LLException):
    def __init__(self, errCode, msgPrefix, msg):
        super().__init__(errCode, msgPrefix, msg)

class ParsingException(LLException):
    def __init__(self, errCode, msgPrefix, msg):
        super().__init__(errCode, msgPrefix, msg)

class GrammarLexicalException(GrammarException):
    def __init__(self, line, msg):
        super().__init__(110, f"L{line} Lexical Error", msg)

class GrammarNotLL1Exception(LLException):
    def __init__(self, nonterminal, terminal, rule1, rule2):
        super().__init__(120, f"Provided grammar is not an LL(1) grammar", f'Both "{rule1}" and "{rule2}" can derive "{nonterminal}/{terminal}"')

class ParsingSyntaxException(ParsingException):
    def __init__(self, msg):
        super().__init__(220, f"Syntax errror in input", msg)

class ParsingActionMissingException(ParsingException):
    def __init__(self, rule):
        super().__init__(250, f"Missing an action for a rule encountered during derivation", rule)

class ParsingLexicalException(ParsingException):
    def __init__(self, msg):
        super().__init__(210, f"Lexical Error in input", msg)