from llgram.generation import TableGenerator
from llgram.parsing import LLParser

with open("testGrammar2.txt", "r") as fin:
    generator = TableGenerator(fin.read())

table = generator.getParsingTable()
startingSymbol = generator.getStartSymbol()
rules = generator.getRules()

actions = {rule:None for rule in rules}

actions["A -> c"] = lambda : print("Hello!")

parser = LLParser(table, startingSymbol, actions)

with open("testInput.txt", "r") as fin:
    derivation = parser.parse(fin.read().split(), execute=True, explicitActions=True, actions=actions)

print(derivation)