#!/usr/bin/env bash
set -euo pipefail

# Usage:  bash install_pi_zero2w.sh  [PROJECT_DIR]
# Default PROJECT_DIR is $HOME/Open_Duck_Mini_Runtime
PROJECT_DIR="${1:-$HOME/Open_Duck_Mini_Runtime}"

echo "==> Using PROJECT_DIR: $PROJECT_DIR"

# 0) Add 2G swap if not present (safe & idempotent)
if ! swapon --show | grep -q 'partition\|file'; then
  echo "==> No active swap detected; creating 2G swapfile at /swapfile"
  sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  if ! grep -q '^/swapfile ' /etc/fstab; then
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
  fi
else
  echo "==> Swap already active:"
  swapon --show || true
fi

echo "==> Memory status:"
free -h || true

# 1) Larger temp & cache for pip
mkdir -p "$HOME/tmp" "$HOME/pip-cache"
export TMPDIR="$HOME/tmp"
export PIP_CACHE_DIR="$HOME/pip-cache"
export PIP_ONLY_BINARY=":all:"
export PIP_NO_COMPILE="1"

# 2) Use current Python/venv
PY="${PYTHON:-python}"
PIP="$PY -m pip"

echo "==> Python: $($PY -V)"
echo "==> Pip:    $($PIP --version)"
echo "==> Pip cache: $PIP_CACHE_DIR   TMPDIR: $TMPDIR"

# Optional: clear cache to cut peak disk usage
$PIP cache purge || true

# 3) Install heavy wheels first (exact versions known to have cp313/aarch64 wheels)
echo "==> Installing numpy/scipy/onnxruntime wheels..."
$PIP install --no-cache-dir --prefer-binary \
  numpy==2.2.6 scipy==1.15.1 onnxruntime==1.23.2

# 4) Install pygame; try default index, then fall back to piwheels if needed
echo '==> Installing pygame==2.6.1 (wheel only)...'
if ! $PIP install --no-cache-dir --prefer-binary pygame==2.6.1; then
  echo '!! Default index failed for pygame; trying piwheels...'
  $PIP install --no-cache-dir --prefer-binary -i https://www.piwheels.org/simple pygame==2.6.1 || echo '!! Skipping pygame for now.'
fi

# 5) Pre-install pypot without build isolation and without deps (avoid big transitive wheels)
echo "==> Installing pypot from git (no build isolation / no deps)..."
$PIP install --no-cache-dir --no-build-isolation --no-deps \
  "git+https://github.com/pollen-robotics/pypot@support-feetech-sts3215"

# 6) Manually install pypot runtime deps (lightweight first)
echo "==> Installing pypot runtime dependencies..."
$PIP install --no-cache-dir bottle tornado requests pyserial ikpy==3.0.1 wget

# If you really need OpenCV, install headless (lighter). Switch to opencv-contrib-python only if required.
echo "==> Installing OpenCV (headless)..."
$PIP install --no-cache-dir --prefer-binary opencv-python-headless

# 7) Finally install your project (do NOT resolve deps again)
echo "==> Installing the project (editable, no deps): $PROJECT_DIR"
$PIP install --no-deps --no-cache-dir -e "$PROJECT_DIR"

# 8) Sanity check
echo "==> Sanity check:"
$PY - <<'PY'
import sys
print("Python:", sys.version.split()[0])
def safe(mod, attr=None):
    try:
        m = __import__(mod)
        if attr:
            print(f"{mod}:", getattr(m, attr, 'OK'))
        else:
            print(f"{mod} OK")
    except Exception as e:
        print(f"{mod} FAIL -> {e}")
for mod, attr in [
    ("numpy","__version__"),
    ("scipy","__version__"),
    ("onnxruntime","__version__"),
    ("pygame", None),
    ("pypot", None),
    ("cv2", None),
]:
    safe(mod, attr)
PY

echo "==> Done."
