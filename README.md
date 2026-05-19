# Opus X

App de fitness — single-file HTML hospedado em GitHub Pages.

Site: <https://ewertondecastro.github.io/opusx/>

## Como funciona o auto-update

1. O `index.html` tem uma `<meta name="app-version">` com timestamp.
2. Quando o app abre no celular, ele busca o `index.html` mais recente do GitHub e compara as versões.
3. Se a versão remota mudou, um banner aparece pedindo pra atualizar.
4. Ao clicar **Atualizar**, o cache é limpo e a página recarrega na versão nova.

A meta é atualizada automaticamente pelo `auto-push.sh` toda vez que ele detecta uma mudança e dá push.

## Auto-push local → GitHub

### Modo manual (rodar em terminal)
```bash
./scripts/auto-push.sh
```
Deixe rodando em uma aba. Ele vigia o `index.html`, espera 20s sem mudança e dá `commit` + `push` sozinho. `Ctrl+C` pra parar.

### Modo "sempre ligado" (instalar como serviço do macOS)
```bash
./scripts/install-auto-push.sh
```
Vai rodar no boot e ficar vigiando em background. Logs em `logs/`.

Parar: `launchctl unload ~/Library/LaunchAgents/com.decastro.opusx.autopush.plist`
