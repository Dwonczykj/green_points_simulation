#!/bin/bash --login
# The --login ensures the bash configuration is loaded,
# enabling Conda.

# Enable strict mode.
set -euo pipefail
# ... Run whatever commands ...

# Temporarily disable strict mode and activate conda:
set +euo pipefail
conda activate myenv

# Re-enable strict mode:
set -euo pipefail

# exec the final command:
# exec python run.py
exec gunicorn -b :5000 --access-logfile - --error-logfile - app:run_app