#!/bin/bash
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews-singleton/corpus_airbus --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews-singleton/corpus_apple --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews-singleton/corpus_gm_chrysler_ford --format conll
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder corefgraph-conll-wikinews-singleton/corpus_stock_market --format conll
