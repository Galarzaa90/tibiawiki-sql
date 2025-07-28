#!/bin/bash
set -e

echo "🐳 Building local Docker image..."
docker build --pull -t tibiawiki-sql .

echo "🗃️  Preparing files..."
touch tibiawiki.db
mkdir -p images

# Handle Git Bash on Windows vs Linux/macOS
case "$OSTYPE" in
  msys*|cygwin*)
    WORKDIR=$(pwd -W)
    ;;
  *)
    WORKDIR=$(pwd)
    ;;
esac

echo "🚀 Running tibiawiki-sql container..."
docker run \
  -v "$WORKDIR/tibiawiki.db:/usr/src/app/tibiawiki.db" \
  -v "$WORKDIR/images:/usr/src/app/images" \
  -ti --rm tibiawiki-sql -sd
