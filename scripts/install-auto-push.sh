#!/usr/bin/env bash
# install-auto-push.sh — instala o auto-push como serviço de fundo do macOS (launchd)
# Roda sozinho no boot do Mac e fica vigiando o index.html.
set -e
cd "$(dirname "$0")/.."
PROJECT="$(pwd)"
PLIST_LABEL="com.decastro.opusx.autopush"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
mkdir -p "$HOME/Library/LaunchAgents" logs

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${PROJECT}/scripts/auto-push.sh</string>
  </array>
  <key>WorkingDirectory</key><string>${PROJECT}</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>${PROJECT}/logs/auto-push.out.log</string>
  <key>StandardErrorPath</key><string>${PROJECT}/logs/auto-push.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
echo "Instalado: $PLIST_PATH"
echo "Logs:      $PROJECT/logs/auto-push.{out,err}.log"
echo "Parar:     launchctl unload \"$PLIST_PATH\""
echo "Voltar:    launchctl load   \"$PLIST_PATH\""
