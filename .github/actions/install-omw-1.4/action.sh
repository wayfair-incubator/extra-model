set -euo pipefail

echo "Installing nltk data package"
python -m nltk.downloader download ${NLTK_DATA_PACKAGE}
