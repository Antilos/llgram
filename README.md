# llgram
llgram is a tool for generating ll(1) grammar parsing tables. It uses it's own grammar language and can export the table as both a json and a pickled python object

# llgram grammar language
llgram expects a grammar in the following language:
+ A single line can contain a starting symbol. This line shall have the following form: "-> &lt;symbol>". If this line is omitted, the first nonterminal symbol will be considered the starting symbol. Multiple lines of this format will result in an error.
+ Every other line contains a single rewriting rule.
+ The rules look as follows:
 + "&lt;symbol> -> &lt;symbol> &lt;symbol> ..."
 + Where &lt;symbol> is any alphanumerical string, excluding the following: "epsilon", "->", "__$".
 + Symbols shall be separated by a sequence of whitespace characters.
 + The reserved string "epsilon" will be interpreted as an empty string.
+ Every symbol that appears on the left of at least one rule is considered a nonterminal. Every other symbol is considered a terminal. There is no restriction on the form terminal and nonterminal symbols can take.
+ Lines starting with "#" will be ignored by the parser and can be used for comments. Inline comments are not currently supported.

## Example of grammar
```
E -> T E2
E2 -> + T E2
E2 -> epsilon
-> E
T -> F T2
T2 -> * F T2
T2 -> epsilon
F -> ( E )
F -> id
```
