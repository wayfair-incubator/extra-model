The workflow follows the algorithm suggested in the paper and has following stages:

### Filtering (`_filter.py`)
Get rid of cruft in the input data:

*  empty text fields
*  requires at least 20 characters of text
*  remove unprintable unicode characters
*  filter for english language using Googles `cld2` tool

### Generate aspects (`_aspects.py`)
Extracts promising phrases (i.e., nouns described by adjectives) using `spacy`.

### Aggregate aspects into topics (`_topics.py`)
Takes the output of the phrase extraction, maps them to `wordnet` (via `_disambiguate.py`) and produces the list of clustered aspects
important dependencies:

* `sklearn` for clustering
* `nltk` for the `wordnet`
* `networkx` for the semantic tree
* pretrained word-vectors (via `_vectorizer.py`)
* `vaderSentiment` for sentiment analysis

### Analyze descriptors (`_adjectives.py`)
Cluster the associated adjectives using constant radius clustering. 

### Link information (`_summarize.py`)
To make the output more useful, we want to link the topics back to the original texts and vice versa.

The whole code produces one csv file.
