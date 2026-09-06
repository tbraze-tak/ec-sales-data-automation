#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "$0")/.." && pwd)
smoke_root=$(mktemp -d /tmp/csv-data-bridge-app.XXXXXX)
trap 'rm -rf "$smoke_root"' EXIT

cp -R "$project_root" "$smoke_root/project"
rm -rf "$smoke_root/project/.git" "$smoke_root/project/.venv" "$smoke_root/project/outputs"
python3 -m venv "$smoke_root/venv"
"$smoke_root/venv/bin/python" -m pip install "$smoke_root/project[app]"
PYTHONPATH="$smoke_root/project/src" "$smoke_root/venv/bin/python" -m unittest discover -s "$smoke_root/project/tests" -q
PYTHONPATH="$smoke_root/project/src" "$smoke_root/venv/bin/python" "$smoke_root/project/scripts/build_mvp_demo.py"

"$smoke_root/venv/bin/python" -m streamlit run "$smoke_root/project/app.py" \
  --server.headless true --server.port 8503 --browser.gatherUsageStats false \
  >"$smoke_root/streamlit.log" 2>&1 &
app_pid=$!
trap 'kill "$app_pid" 2>/dev/null || true; rm -rf "$smoke_root"' EXIT
for attempt in 1 2 3 4 5; do
  if curl --fail --silent http://localhost:8503/_stcore/health >/dev/null; then
    break
  fi
  sleep 2
done
curl --fail --silent http://localhost:8503/_stcore/health >/dev/null
kill "$app_pid"
wait "$app_pid" 2>/dev/null || true
echo "Clean application install smoke test passed"
