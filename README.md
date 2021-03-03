[![codecov](https://codecov.io/gh/wayfair-incubator/extra-model/branch/main/graph/badge.svg?token=HXSGN5IUzu)](https://codecov.io/gh/wayfair-incubator/extra-model)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

TODO: update badges

# extra-model

Code to run the Extra [algorithm](https://www.aclweb.org/anthology/D18-1384/) for unsupervised topic/aspect extraction on English texts.

## Quick start

**IMPORTANT**: 
1. When running Extra inside docker-container, make sure that Docker process has enough resources. 
For example, on Mac/Windows it should have at least 8 Gb of RAM available to it.
1. GitHub repo does **not** come with Glove Embeddings. See the next section for how to download the reuired embeddings.

### Downloading Embeddings

**This package does not come with the required Glove embeddings and they must be downloaded before use.**

To download the required embeddings, run the following command:

```bash
docker-compose run --rm setup
```

The embeddings will be downloaded, unzipped and formatted into a space-efficient format. Files will be saved in the `embeddings/` directory in the root of the project directory. If the process fails, it can be safely restarted. If you want to restart the process with new files, delete all files except `README.md` in the `embeddings/` directory.

### Using docker-compose

First, build the image:

```bash
docker-compose build
```

Then running `extra-model` is as simple as:

```bash
docker-compose run extra-model /package/tests/resources/100_comments.csv
```

NOTE: when using this approach, input file should be mounted inside the container.
By default, everything from `extra-model` folder will be mounted to `/package/` folder. 
This can be changed in `docker-compose.yaml`

This will produce a `result.csv` file in `/io/` (default setting) folder. 

Location of the output can be changed by supplying second path, e.g.:

```bash
docker-compose run extra-model /package/tests/resources/100_comments.csv /io/another_folder
```

### Using command line

TODO: add this section.

## `extra-model` input

Input of an extra is a `.csv` file with 2 columns: `CommentId` and `Comments`. 
Both must be present and named exactly in that way.

## `extra-model` output

After `extra-model` finishes calculations, it'll produce a `.csv` file with following structure:

```text
AdCluster,Aspect,AspectCount,CommentId,Descriptor,Position,SentimentBinary,SentimentCompound,Topic,TopicCount,TopicImportance,TopicSentimentBinary,TopicSentimentCompound,WordnetNode
only,downside,1,321,only,9,0.0,0.0,downside.n.01,1,0.005572645018795278,0.0,0.0,downside.n.01
more,nothing,1,74,more,54,0.0,0.0,nothing.n.01,1,0.005572645018795278,0.0,0.0,nothing.n.01
clean,bathrooms,1,146,clean,4,1.0,0.4019,toilet.n.01,1,0.005572645018795278,1.0,0.4019,toilet.n.01
decorated,place,5,146,decorated,32,0.0,0.0,home.n.01,6,0.03343587011277168,0.0,-0.01131666666666666,home.n.01
```

Columns have following meaning:

|Column                      | Description |
|:----------------------|:----------------------|
|AdCluster              |Adjectives are clustered together and this indicates the "center" of a cluster (e.g., "awesome", "fantastic", "great" descriptors might produce "great" as `AdCluster`)|
|Aspect                 |Identified aspect - this is an actual word that person wrote in a text|
|AspectCount            |How often this aspect has been found in all of the input|
|CommentId              |`ID` of an input. Since one input may produce multiple aspects, `ID` column must always be present|
|Descriptor             |Identified adjective (not clustered) - this is an actual word that person wrote in a text|
|Position               |Character number where aspect was found (e.g., "nice shirt" will have aspect "shirt" and `Position` 6|
|SentimentBinary        |Binary sentiment for aspect|
|SentimentCompound      |Compound sentiment for aspect|
|Topic                  |Collection of aspects.|
|TopicCount             |How often topic has been found in input|
|TopicImportance        |Importance of a topic|
|TopicSentimentBinary   |Similar to aspect, but on a topic level|
|TopicSentimentCompound |Similar to aspect, but on a topic level|
|WordnetNode            |Mapping to `wordnet` node. Identifiers in the form `.n.01` mean first meaning of the noun in `wordnet`| 


## Extra workflow

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

## CI

TODO: update this section

This project comes with a GitHub Actions pipeline definition. 

## Develop

First, please [install docker](https://docs.docker.com/install/) on your computer.
Docker must be running correctly for these commands to work. 

* If you are using windows, please make sure your editor writes files with the linefeed (`\n`) line endings.*

Next, clone the repo:

TODO: update this

```bash
git clone 
cd extra-model
```

Then run the test suite to see if docker is set up correctly:

```bash
docker-compose run test
```

## Testing

You'll be unable to merge code unless the linting and tests pass. You can run these in your container via `docker-compose run test`.

The tests, linting, and code coverage are run automatically via CI, and you'll see the output on your pull requests.

Generally we should endeavor to write tests for every feature. 
Every new feature branch should increase the test coverage rather than decreasing it.

We use [pytest](https://docs.pytest.org/en/latest/) as our testing framework.

To test/lint your project, you can run `docker-compose run test`.

#### Stages

TODO: update this 

To customize / override a specific testing stage, please read the documentation specific to that tool:

1. PyTest: [https://docs.pytest.org/en/latest/contents.html](https://docs.pytest.org/en/latest/contents.html)
1. Black: [https://black.readthedocs.io/en/stable/](https://black.readthedocs.io/en/stable/)
1. Flake8: [http://flake8.pycqa.org/en/latest/](http://flake8.pycqa.org/en/latest/)
1. Bandit: [https://bandit.readthedocs.io/en/latest/](https://bandit.readthedocs.io/en/latest/)
1. iSort: [https://pycqa.github.io/isort/](https://pycqa.github.io/isort/)
1. pydocstyle: [http://www.pydocstyle.org/en/stable/](http://www.pydocstyle.org/en/stable/)

  
## Documentation

TODO: change to sphinx site:

Check out the [project documentation]().

# Authors

`extra-model` was written by `mbalyasin@wayfair.com`, `mmozer@wayfair.com`.
