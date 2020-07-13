from llgram.generation import TableGenerator
import logging

finName = "testGrammar.txt"

with open(finName, "r") as fin:
    generator = TableGenerator(fin.read())

    with open("testTable.json", "w") as fout:
        generator.printParsingTableAsJson(fout)

