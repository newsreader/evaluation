#!/bin/bash
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews/corpus_airbus --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews/corpus_apple --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews/corpus_gm_chrysler_ford --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews/corpus_stock_market --format conll
