#!/bin/bash

REPO_PATH=$1
cd "$REPO_PATH" || { echo "Hibás útvonal: $REPO_PATH"; exit 1; }

echo "Átállás indul itt: $REPO_PATH"

# 1. Ellenőrzés, hogy master ágon vagyunk
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
if [[ "$CURRENT_BRANCH" != "master" ]]; then
  echo "Nem master ágon vagyunk, kihagyva..."
  exit 0
fi

# 2. Átnevezés
git branch -m master main
git push -u origin main

# 3. Átállítás GitHub-on (gh CLI szükséges)
if command -v gh &> /dev/null; then
  gh repo set-default-branch main
else
  echo "⚠️  'gh' CLI nincs telepítve, kézzel állítsd át GitHub-on az alapértelmezett branchet!"
fi

# 4. Opcionális törlés
read -p "Töröljük a remote 'master' branchet? (igen/nem): " CONFIRM
if [[ "$CONFIRM" == "igen" ]]; then
  git push origin --delete master
fi

echo "✅ Kész: $REPO_PATH → main"
