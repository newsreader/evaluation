#!/bin/bash

java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key gold-standard/corpus_airbus/
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key gold-standard/corpus_apple/
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key gold-standard/corpus_gm_chrysler_ford/
java -cp coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key gold-standard/corpus_stock_market/
