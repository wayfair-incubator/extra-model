set -euo pipefail

# requirements.txt pins the en_core_web_sm spacy pipeline as a direct URL against
# github.com's release downloads, which intermittently serves 503s. pip's own retries
# all fire within a few seconds, which is too fast to ride out a flap, so retry with
# real backoff on top.
pip_install() {
  local attempt
  for attempt in 1 2 3 4; do
    if pip install --retries 5 --timeout 30 "$@"; then
      return 0
    fi
    if [[ "${attempt}" -lt 4 ]]; then
      local delay=$((attempt * 20))
      echo "pip install failed (attempt ${attempt}), retrying in ${delay}s..."
      sleep "${delay}"
    fi
  done
  echo "pip install still failing after 4 attempts"
  return 1
}

echo "Ensuring pip is up to date"
python -m pip install --upgrade pip

if [[ "${INSTALL_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing code requirements"
  pip_install -r requirements.txt
fi

if [[ "${INSTALL_TEST_REQUIREMENTS}" == "true"  ]]; then
  echo "Installing test requirements"
  pip_install -r requirements-test.txt
fi
