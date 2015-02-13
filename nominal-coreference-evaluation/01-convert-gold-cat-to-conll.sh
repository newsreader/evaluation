#!/bin/bash

java -cp ~/javacode/newsreader/coreference-conll-evaluation/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type ENTITY --file-extension .xml --folder ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_airbus/ --format conll
java -cp ~/javacode/newsreader/coreference-conll-evaluation/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type ENTITY --file-extension .xml --folder ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_apple/ --format conll
java -cp ~/javacode/newsreader/coreference-conll-evaluation/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type ENTITY --file-extension .xml --folder ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_gm_chrysler_ford/ --format conll
java -cp ~/javacode/newsreader/coreference-conll-evaluation/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type ENTITY --file-extension .xml --folder ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_stock_market/ --format conll

mv ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_airbus/*.key ~/javacode/newsreader/coreference-conll-evaluation/gold-standard/corpus_airbus/
mv ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_apple/*.key ~/javacode/newsreader/coreference-conll-evaluation/gold-standard/corpus_apple/
mv ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_gm_chrysler_ford/*.key ~/javacode/newsreader/coreference-conll-evaluation/gold-standard/corpus_gm_chrysler_ford/
mv ~/javacode/newsreader/piek-coref-evaluation/corpus_CAT_GS_201412/corpus_stock_market/*.key ~/javacode/newsreader/coreference-conll-evaluation/gold-standard/corpus_stock_market/

