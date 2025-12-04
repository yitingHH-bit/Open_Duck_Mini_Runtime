#!/usr/bin/env bash
set -euo pipefail

# Usage: bash install_pi_zero2w_v2.sh [PROJECT_DIR] [SWAP_GB]
# Defaults: PROJECT_DIR=$HOME/Open_Duck_Mini_Runtime SWAP_GB=4
PROJECT_DIR="${1:-$HOME/Open_Duck_Mini_Runtime}"
SWAP_GB="${2:-4}"

echo "==> Using PROJECT_DIR: $PROJECT_DIR"
echo "==> Target swap size: ${SWAP_GB}G (will add /swapfile if needed, even if zram is active)"

# 0) Ensure at least SWAP_GB swap total by adding a swapfile (keep zram if any)
current_kb=$(grep -i '^SwapTotal:' /proc/meminfo | awk '{print $2}')
current_mb=$(( (current_kb + 1023) / 1024 ))
target_mb=$(( SWAP_GB * 1024 ))
echo "==> Current swap total: ${current_mb} MiB"
if [ "$current_mb" -lt "$target_mb" ]; then
  add_mb=$(( target_mb - current_mb ))
  echo "==> Adding swapfile of ${add_mb} MiB at /swapfile"
  sudo fallocate -l ${add_mb}M /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=${add_mb}
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  if ! grep -q '^/swapfile ' /etc/fstab; then
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
  fi
else
  echo "==> Swap total already >= target; keeping existing swap."
fi

echo "==> Memory status after swap:"
free -h || true
swapon --show || true

# 1) Larger temp & cache for pip
mkdir -p "$HOME/tmp" "$HOME/pip-cache"
export TMPDIR="$HOME/tmp"
export PIP_CACHE_DIR="$HOME/pip-cache"
export PIP_ONLY_BINARY=":all:"
export PIP_NO_COMPILE="1"

PY="${PYTHON:-python}"
PIP="$PY -m pip"

echo "==> Python: $($PY -V)"
echo "==> Pip:    $($PIP --version)"
$PIP cache purge || true

step() { echo -e "\n==== $* ====\n"; }

# 2) Install wheels strictly one-by-one to minimize peak RSS
step "Install numpy (wheel only, no deps)"
$PIP install --no-cache-dir --only-binary=:all: --no-deps numpy==2.2.6
free -h || true

step "Install scipy (wheel only, no deps)"
$PIP install --no-cache-dir --only-binary=:all: --no-deps scipy==1.15.1
free -h || true

step "Install onnxruntime (wheel only, no deps)"
$PIP install --no-cache-dir --only-binary=:all: --no-deps onnxruntime==1.23.2
free -h || true

step "Install onnxruntime's light deps"
$PIP install --no-cache-dir coloredlogs flatbuffers packaging protobuf sympy
free -h || true

step "Install pygame (wheel only); fallback to piwheels if needed"
if ! $PIP install --no-cache-dir --only-binary=:all: --prefer-binary pygame==2.6.1; then
  $PIP install --no-cache-dir -i https://www.piwheels.org/simple pygame==2.6.1 || echo "!! Skipping pygame"
fi
free -h || true

step "Install pypot from git (no build isolation / no deps)"
$PIP install --no-cache-dir --no-build-isolation --no-deps \
  "git+https://github.com/pollen-robotics/pypot@support-feetech-sts3215"
free -h || true

step "Install pypot runtime deps (light)"
$PIP install --no-cache-dir bottle tornado requests pyserial ikpy==3.0.1 wget
free -h || true

step "Install OpenCV (headless)"
$PIP install --no-cache-dir --prefer-binary opencv-python-headless
free -h || true

step "Install project (editable, no deps): $PROJECT_DIR"
$PIP install --no-deps --no-cache-dir -e "$PROJECT_DIR"

step "Sanity check"
$PY - <<'PY'
import sys
print("Python:", sys.version.split()[0])
def safe(mod, attr=None):
    try:
        m = __import__(mod)
        print(f"{mod}:", getattr(m, attr) if attr else "OK")
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
