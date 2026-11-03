#!/usr/bin/env bash
# PreToolUse (matcher: Bash). Se o comando for um runner de testes "simples", reescreve-o para
# passar por quiet-run.sh. Qualquer outro comando passa intacto ({}).
#
# O padrao e deliberadamente restrito: sem ; & | < > ` $ # \ nem caracteres de controle,
# para nunca reescrever pipelines ou comandos compostos do usuario.
set -u
input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

pattern='^(npm test|npm run test|pnpm test|pnpm run test|yarn test|npx vitest|npx jest|vitest|jest|pytest|python -m pytest|python3 -m pytest|go test|cargo test|mvn test|gradle test|\./gradlew test|dotnet test|bundle exec rspec|rspec|phpunit|mix test)( [^;&|<>`$#\\[:cntrl:]]*)?$'

if [[ -n "$cmd" && "$cmd" =~ $pattern ]]; then
  wrapper="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/quiet-run.sh"   # ao lado deste script
  [ -x "$wrapper" ] || { echo '{}'; exit 0; }   # sem wrapper instalado: nao mexe em nada
  novo="$wrapper $(printf '%s' "$cmd" | jq -Rr '@sh')"
  printf '%s' "$input" | jq --arg novo "$novo" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", updatedInput: (.tool_input + {command: $novo})}}'
else
  echo '{}'
fi
