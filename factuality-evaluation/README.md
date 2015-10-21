factuality evaluation
=====================

factuality_to_conll.py

takes a naf file with token, term, factuality and srl layer as input and prints a conll representation of tokens with event indication and factuality values as output.

token termid event polarity certainty time
President t1 O O O O
Barack t2 O O O O
Obama t3 O O O O
puts t4 B-EVENT POS CERTAIN NON_FUTURE
on t5 I-EVENT POS CERTAIN NON_FUTURE

Dependency:

* KafNafParserPy:

https://github.com/cltl/KafNafParserPy

Running the module:

cat input.naf | python factuality_to_conll.py > output_conll.txt
