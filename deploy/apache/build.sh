set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
OPTS="--no-cache --platform linux/amd64,linux/arm64"
#OPTS=

IMAGE=harbor.us.lmco.com/lmc.space.ai/apache-ssl
docker build $OPTS -t "$IMAGE" .

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "ERROR: image $IMAGE was not built"
  exit 1
fi

CREATED_AT=$(docker image inspect -f '{{.Created}}' "$IMAGE")
IMAGE_AGE_SECONDS=$(IMAGE_CREATED_AT="$CREATED_AT" python3 - <<'PY'
from datetime import datetime, timezone
import os

created_at = datetime.fromisoformat(os.environ["IMAGE_CREATED_AT"].replace("Z", "+00:00"))
now = datetime.now(timezone.utc)
print(int((now - created_at).total_seconds()))
PY
)

if [ "$IMAGE_AGE_SECONDS" -gt 5 ]; then
  echo "Image is old ($IMAGE_AGE_SECONDS seconds); skipping push"
  exit 0
fi

#docker tag $IMAGE $IMAGE
docker login -u $HELM_ROBO_USER -p $HELM_ROBO_PASS harbor.us.lmco.com
docker push "$IMAGE"

echo "To run"
echo 'docker network ls | grep demonet ; if [ "$?" != "0" ]; then docker network create demonet ; fi'
echo "docker run -d -p 80:80 -p 443:443 --network demonet --rm --name apache $IMAGE"
