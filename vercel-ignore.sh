#!/bin/sh
# Vercel "Ignored Build Step" (vercel.json: ignoreCommand).
# Exit 0: skip the build. Exit 1 (or any other code): build.
#
# Build only when a file that goes into the web site changed since the last deployment of this branch.
# Brand files that the site does not use (brand book, generator, social media graphics, photos),
# raw sources and documentation do not start a build.
#
# If build.mjs starts to read a new file or folder, add it to the list below.

BASE="${VERCEL_GIT_PREVIOUS_SHA:-HEAD^}"

git diff --quiet "$BASE" HEAD -- \
  build.mjs \
  package.json \
  package-lock.json \
  vercel.json \
  vercel-ignore.sh \
  site \
  wiki \
  marka/tokens.json \
  marka/svg \
  marka/png \
  marka/media-spolecznosciowe/facebook-tlo-jasna.png
STATUS=$?

case $STATUS in
  0) echo "No change in web site files since $BASE: build skipped." ;;
  1) echo "Web site files changed since $BASE: building." ;;
  *) echo "Cannot compare with $BASE: building." ;;
esac

# git diff --quiet: 0 = no change (skip), 1 = change (build), other = error (build)
exit $STATUS
