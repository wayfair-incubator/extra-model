set -euo pipefail

echo "Installing spacy language package"
python -m spacy download ${SPACY_LANGUAGE_PACKAGE}
