export DOCKER=docker

export IMAGE=harbor.us.lmco.com/lmc.space.ai/aiapp

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

BUILD_ONLY=0
if [ "${1:-}" = "0" ]; then
  BUILD_ONLY=1
fi

# 1. Build the image with proper tag
$DOCKER build --no-cache \
  --build-context djangoui=../djangoui \
  --build-arg EFOSS_USER="$EFOSS_USER" \
  --build-arg EFOSS_TOKEN="$EFOSS_TOKEN" \
  --platform=linux/amd64 \
  -f deploy/docker1 \
  -t $IMAGE:latest \
  .

# 2. Verify the image was built
if ! $DOCKER image inspect $IMAGE:latest >/dev/null 2>&1; then
  echo "ERROR: image $IMAGE:latest was not built"
  exit 1
fi

CREATED_AT=$($DOCKER image inspect -f '{{.Created}}' $IMAGE:latest)
IMAGE_AGE_SECONDS=$(IMAGE_CREATED_AT="$CREATED_AT" python3 - <<'PY'
from datetime import datetime, timezone
import os

created_at = datetime.fromisoformat(os.environ["IMAGE_CREATED_AT"].replace("Z", "+00:00"))
now = datetime.now(timezone.utc)
print(int((now - created_at).total_seconds()))
PY
)

if [ "$IMAGE_AGE_SECONDS" -gt 20 ]; then
  echo "ERROR: image $IMAGE:latest is stale ($IMAGE_AGE_SECONDS seconds old); current build likely failed"
  exit 1
fi

if [ "$IMAGE_AGE_SECONDS" -le 5 ]; then
  echo "Verified fresh image age: $IMAGE_AGE_SECONDS seconds"
else
  echo "Verified image age: $IMAGE_AGE_SECONDS seconds"
fi

$DOCKER image ls | grep -F "$IMAGE"

if [ "$BUILD_ONLY" -eq 1 ]; then
  echo "Build-only mode enabled; skipping Harbor login and push"
  exit 0
fi

# 3. Login to Harbor
$DOCKER login -u $HELM_ROBO_USER -p $HELM_ROBO_PASS harbor.us.lmco.com
# 4. Push to Harbor
$DOCKER push $IMAGE:latest

# 5. Verify the push succeeded (optional)
# You can check in the Harbor web UI at:
# https://harbor.us.lmco.com/harbor/projects/[project-id]/repositories

