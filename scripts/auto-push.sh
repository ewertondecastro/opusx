#!/usr/bin/env bash
# auto-push.sh — vigia index.html e dá commit+push automático no GitHub
# uso: ./scripts/auto-push.sh   (deixa rodando numa aba do terminal)
set -u
cd "$(dirname "$0")/.."

FILE="index.html"
POLL=5            # checa a cada 5s
DEBOUNCE=20       # espera 20s sem mudança antes de pushar
LOCK=".auto-push.lock"

if [ -f "$LOCK" ]; then
  echo "[auto-push] já está rodando (lock: $LOCK). Rode 'rm $LOCK' se travou."
  exit 1
fi
trap 'rm -f "$LOCK"; echo "[auto-push] parado."; exit 0' INT TERM EXIT
echo $$ > "$LOCK"

get_mtime(){ stat -f %m "$1" 2>/dev/null || echo 0; }

bump_version(){
  # substitui o conteúdo da meta app-version pelo timestamp ISO-UTC atual
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  # sed in-place compatível com macOS
  sed -i '' -E "s|(<meta name=\"app-version\" content=\")[^\"]*(\">)|\1${ts}\2|" "$FILE"
  echo "$ts"
}

echo "[auto-push] vigiando $FILE — Ctrl+C pra parar"
LAST_MTIME=$(get_mtime "$FILE")
PENDING_SINCE=0

while true; do
  sleep "$POLL"
  NOW_MTIME=$(get_mtime "$FILE")

  if [ "$NOW_MTIME" != "$LAST_MTIME" ]; then
    LAST_MTIME=$NOW_MTIME
    PENDING_SINCE=$(date +%s)
    echo "[auto-push] mudança detectada — aguardando $DEBOUNCE s de inatividade…"
    continue
  fi

  if [ "$PENDING_SINCE" -gt 0 ]; then
    ELAPSED=$(( $(date +%s) - PENDING_SINCE ))
    if [ "$ELAPSED" -ge "$DEBOUNCE" ]; then
      # se nada pra commitar, reseta e segue
      if git diff --quiet -- "$FILE" && git diff --cached --quiet -- "$FILE"; then
        PENDING_SINCE=0
        continue
      fi
      VER="$(bump_version)"
      # incluir o bump da meta no mesmo commit
      git add "$FILE"
      MSG="update: $VER"
      if git commit -m "$MSG" >/dev/null 2>&1; then
        if git push origin main 2>&1 | tail -3; then
          echo "[auto-push] push ok ($VER)"
        else
          echo "[auto-push] push falhou — verifique conexão / credenciais"
        fi
      else
        echo "[auto-push] nada pra commitar (provavelmente só whitespace)"
      fi
      PENDING_SINCE=0
    fi
  fi
done
