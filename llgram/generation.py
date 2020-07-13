import re
import logging
import json

from llgram import llexceptions as lle

logger = logging.getLogger('simple')
logger.setLevel(logging.CRITICAL)

class TableGenerator:
    def __init__(self, grammar):
        """
            This object reads a grammar in the argument grammar and creates a parsing table.
            If the provided grammar isn't LL(1) grammar, an exception is thrown.

            Parameters
            ----------
            fin : str
                string containing an input grammar in a compatible format.

            Raises
            ------
            GrammarNotLL1Exception
                If the provided grammar is not LL(1)
        """
        lexer = Lexer()

        self.__EPSILON_SYMBOL = "epsilon" #epsilon constant
        self.__END_SYMBOL = "__$"

        self.__terminals = set()
        self.__nonterminals = set()
        self.__rules, self.__startSymbol = lexer.scanRules(grammar)

        self.__table = None

        #find the terminal and nonterminal sets
        #find the nonterminals (symbols on the left)
        for rule in self.__rules:
            if rule.getLeft() not in self.__nonterminals:
                self.__nonterminals.add(rule.getLeft())
        #all symbols on the right that are not nonterminals are terminals
        for rule in self.__rules:
            for symbol in rule.getRight():
                if symbol not in self.__nonterminals:
                    self.__terminals.add(symbol)

        self.__followSets = {nonterminal:set() for nonterminal in self.__nonterminals}
        self.__emptySets = {symbol:False for symbol in self.__nonterminals.union(self.__terminals)} #False if empty, True if it would contain epsilon
        self.__firstSets = {symbol:set() for symbol in self.__nonterminals.union(self.__terminals)}

        #compute empty sets
        self.__computeEmptySets()

        #compute first sets. They are stored in the rules themeselves
        self.__computeSymbolFirstSets()
        self.__computeRuleFirstSets()

        #compute follow sets
        self.__computeFollowSets()

        #compute the table
        self.__computeParsingTable()

    def getAlphabet(self) -> set:
        """
            Returns the alphabet of the provided grammar

            Returns
            -------
            set
                Set of strings representing the symbols in this grammars alphabet
        """
        return self.__nonterminals.union(self.__terminals)

    def getTerminals(self) -> set:
        """
            Returns terminals of the provided grammar

            Returns
            -------
            set
                Set of strings representing the terminals in this grammar
        """
        return self.__terminals

    def getNonterminals(self) -> set:
        """
            Returns nonterminals of the provided grammar

            Returns
            -------
            set
                Set of strings representing the nonterminals in this grammar
        """
        return self.__nonterminals

    def getStartSymbol(self) -> str:
        """
            Returns the start symbol of this grammar

            Returns
            -------
            str
                String representing the starting symbol
        """
        return self.__startSymbol

    def getRuleFirstSets(self) -> dict:
        """
            Returns first sets of the rules (first sets of the left hand side strings).

            Returns
            -------
            dict
                Dictionary with the entire rule string as a key and sets of strings representing the symbols in the first set of that rule as value.
        """
        return {rule:rule.getFirst() for rule in self.__rules}

    def getSymbolFirstSets(self) -> dict:
        """
            Returns first sets for all symbols.

            Returns
            -------
            dict
                Dictionary with symbols as keys and their first sets as values
        """
        return self.__firstSets

    def getFollowSets(self) -> dict:
        """
            Returns follow sets for all nonterminals.

            Returns
            -------
            dict
                Dictionary with nonterminals as keys and their follow sets as values
        """
        return self.__followSets

    def getEmptySets(self) -> dict:
        """
            Returns empty sets for all symbols.

            Returns
            -------
            dict
                Dictionary with symbols as keys and their empty sets as values
        """
        return self.__emptySets

    def __first(self, symbol):
        result = set()
        if symbol in self.__terminals:
            result.add(symbol)
        else:
            for rule in self.__rules:
                if symbol == rule.getLeft():
                    result = result.union(self.__first(rule.getRight()[0]))

        return result

    def __firstOfString(self, string):
        """
        requires first and empty sets of all symbols to be computed first
        """
        result = set()
        for symbol in string:
            if self.__emptySets[symbol]:
                result = result.union(self.__firstSets[symbol])
            else:
                result = result.union(self.__firstSets[symbol])
                break
        return result

    def __computeSymbolFirstSets(self):
        for symbol in self.__firstSets.keys():
            self.__firstSets[symbol] = self.__first(symbol)

    def __computeRuleFirstSets(self):
        """
        Requires empty and first sets for symbols to be computed first
        """
        for rule in self.__rules:
            rhs = rule.getRight()
            result = set()
            for symbol in rhs:
                if self.__emptySets[symbol]:
                    result = result.union(self.__firstSets[symbol])
                else:
                    result = result.union(self.__firstSets[symbol])
                    break
            rule.setFirst(result)

    def __computeEmptySets(self):
        changed = True
        for rule in self.__rules:
            rhs = rule.getRight()
            if len(rhs) == 1 and self.__EPSILON_SYMBOL in rhs:
                self.__emptySets[rule.getLeft()] = True

        while changed:
            changed = False
            for rule in self.__rules:
                rhs = rule.getRight()
                for symbol in rhs:
                    if not self.__emptySets[symbol]:
                        break
                else:
                    self.__emptySets[rule.getLeft()] = True
                    changed = True

    def __emptyOfString(self, string):
        for symbol in string:
            if not self.__emptySets[symbol]:
                break
        else:
            return True
        return False

    def __computeFollowSets(self):
        changed = True
        self.__followSets[self.__startSymbol].add(self.__END_SYMBOL)

        while changed:
            changed = False
            for rule in self.__rules:
                lhs = rule.getLeft()
                rhs = rule.getRight()
                logger.debug(f"Computing from rule: {rule}")
                for i, symbol in enumerate(rhs):
                    if symbol in self.__nonterminals:
                        logger.debug(f"  For symbol: {symbol}. Old follow={self.__followSets[symbol]}")
                        if not(i+1 == len(rhs) or rhs[i+1] == self.__EPSILON_SYMBOL):
                            if self.__followSets[symbol] != self.__followSets[symbol].union(self.__firstOfString(rhs[i+1:]).difference({self.__EPSILON_SYMBOL})):
                                logger.debug(f"    Add First of next ({rhs[i+1]}): {self.__firstOfString(rhs[i+1:])}")
                                self.__followSets[symbol] = self.__followSets[symbol].union(self.__firstOfString(rhs[i+1:]).difference({self.__EPSILON_SYMBOL}))
                                changed = True
                        if self.__emptyOfString(rhs[i+1:]): # Symbol is at the end of production (is followed by an epsilon)
                            logger.debug(f"    Followed by epsilon.")
                            if self.__followSets[symbol] != self.__followSets[symbol].union(self.__followSets[lhs]):
                                logger.debug(f"    Add follow of lhs ({lhs}): {self.__followSets[lhs]}")
                                self.__followSets[symbol] = self.__followSets[symbol].union(self.__followSets[lhs])
                                changed = True
                        logger.debug(f"  New follow={self.__followSets[symbol]}")

    def __computeParsingTable(self):
        self.__table = {nonterminal:{terminal:None for terminal in self.__terminals.difference({self.__EPSILON_SYMBOL}).union({self.__END_SYMBOL})} for nonterminal in self.__nonterminals}

        for nonterminal in self.__nonterminals:
            for terminal in self.__terminals.difference({self.__EPSILON_SYMBOL}).union({self.__END_SYMBOL}):
                for rule in self.__rules:
                    if nonterminal == rule.getLeft():
                        if (terminal in rule.getFirst()) or (self.__EPSILON_SYMBOL in rule.getFirst()) and (terminal in self.__followSets[nonterminal]):
                            if self.__table[nonterminal][terminal] != None:
                                raise lle.GrammarNotLL1Exception(nonterminal, terminal, self.__table[nonterminal][terminal], rule)
                            else:
                                self.__table[nonterminal][terminal] = rule

    def getParsingTable(self):
        return self.__table

    def getParsingTableAsJson(self, indent=4):
        """
            Returns a json string containing the parsing table. The table is json object. Each row is a nonterminal:collum object. Each collum is a terminal:rule object.

            Parameters
            ----------
            indent: int
                indent of the json file, defaults to 4 spaces

            Returns
            -------
            str
                A json string with the parsing table
        """
        return json.dumps(self.__table, default=lambda o:o.__repr__(), indent=indent)

    def printParsingTableAsJson(self, fout, indent=4):
        """
            Prints a json string containing the parsing table to a text file open for writing. The table is a json object. Each row is a nonterminal:collum object. Each collum is a terminal:rule object.

            Parameters
            ----------
            fout : file
                A file open for writing to which to print the table

            indent: int
                indent of the json file, defaults to 4 spaces
        """
        json.dump(self.__table, fout, default=lambda o:o.__repr__(), indent=indent)



class Rule:
    def __init__(self):
        """
            Parameters
            ----------
            left : str
                left hand side of this rule (should only be one token, as these are non-context grammars)
            right : list(str)
                right hand side of the rule (a list of tokens)
        """
        self.left = ""
        self.right = list()
        self.first = set()
        self.follow = set()

    def __repr__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __str__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def getLeft(self):
        return self.left

    def setLeft(self, val):
        self.left = val
    
    def getRight(self):
        return self.right

    def appendRight(self, val):
        self.right.append(val)

    def getFirst(self):
        return self.first

    def addFirst(self, val):
        self.first.add(val)

    def setFirst(self, val):
        self.first = val

    def addFollow(self, val):
        self.follow.add(val)

class Lexer:
    def __init__(self):
        pass

    def __tokenize(self, grammar):
        """
            Tokenizes an input grammar

            Parameters
            ----------
            grammar : str
                String containing the grammar to be scanned.
            
            Returns
            -------
            list
                List of rules, where each element is a list of tokens
        """
        result = list()
        lines = grammar.splitlines(False)

        for line in lines:
            line = line.strip()

            #ignore comments
            if line[0] == "#":
                continue

            result.append(re.split(r"\s+", line))

        return result

    def scanRules(self, grammar: str):
        """
            Performs a lexical analysis of the grammar and returns a list of rules

            Syntax:
                A single line can have the form of "-> symbol", where symbol is the start symbol of this grammar.
                Multiple start symbol lines will result in an error. In the absence of an explicit start symbol, the left hand side of the first rule will be considered the start symbol.

                Every other line should have the form "<nonterminal> -> <symbol1> <symbol2> ..."

                The set of nonterminals is infered as all symbols that appear on the left hand side of at least one rule.
                The set of terminals is infered as any symbol that is not a nonterminal.

            Parameters
            ----------
            grammar : str
                String containing the grammar to be scanned.

            Returns
            -------
            list
                List of rules found in the input grammar
            str
                Start Symbol

            Raises
            ------
            LexicalException
                If the grammar in the input is not lexicaly correct
        """
        lines = self.__tokenize(grammar)
        result = list()

        state = 0

        curRule = Rule()
        startSymbol = ""
        explicitStartSymbol = False
        firstRuleRead = False
        readStartSymbol = False

        for lineCounter, line in enumerate(lines): #line counter is for error reporting purposes
            for token in line:
                if state == 0: #start of line
                    if token == "->":
                        if not explicitStartSymbol:
                            state = 3
                        else:
                            raise lle.LexicalException(lineCounter, "Start symbol can only be defined once.")
                    elif token == "\n":
                        #empty line
                        continue
                    else:
                        state = 1
                        if not firstRuleRead:
                            startSymbol = token
                            firstRuleRead = True
                        curRule.setLeft(token)
                elif state == 1: # one token (left-hand side) read
                    if token == "->":
                        state = 2
                    else:
                        raise lle.LexicalException(lineCounter, "Only one symbol can appear on the left side of a rule.")
                elif state == 2: #reading right-hand side
                    if token == "->":
                        raise lle.LexicalException(lineCounter, "Unexpected symbol '->'.")
                    else:
                        curRule.appendRight(token)
                elif state == 3: #reading start symbol
                    if token == "->":
                        raise lle.LexicalException(lineCounter, "Unexpected symbol '->'.")
                    elif token == "\n":
                        raise lle.LexicalException(lineCounter, "No start symbol provided.")
                    else:
                        startSymbol = token
                        explicitStartSymbol = True
                        readStartSymbol = True
            #EOL
            if not readStartSymbol:
                result.append(curRule)
            curRule = Rule()
            state = 0
            readStartSymbol = False


        return result, startSymbol