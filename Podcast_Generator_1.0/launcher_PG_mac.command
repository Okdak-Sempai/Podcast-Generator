#!/bin/bash
cd "$(dirname "$0")"

if [ ! -f launcher_mac.command ]; then
    echo "[ERREUR] Fichier manquant : launcher_mac.command"
    exit 1
fi

if [ ! -f launcher_server_mac.command ]; then
    echo "[ERREUR] Fichier manquant : launcher_server_mac.command"
    exit 1
fi

# Ouvre chaque script dans un nouveau terminal
osascript <<END
tell application "Terminal"
    do script "cd \"$(pwd)\" && bash launcher_server_mac.command"
end tell
END

osascript <<END
tell application "Terminal"
    do script "cd \"$(pwd)\" && bash launcher_mac.command"
end tell
END
