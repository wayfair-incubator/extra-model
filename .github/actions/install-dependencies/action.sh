set -euo pipefail

echo "Ensuring pip is up to date"
python -m pip install --upgrade pip

if [[ "${INSTALL_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing code requirements"
  pip install -r requirements.txt
  python -m spacy download en_core_web_sm #download spacy language pack
fi

if [[ "${INSTALL_TEST_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing test requirements"
  pip install -r requirements-test.txt
fi
