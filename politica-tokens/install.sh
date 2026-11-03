#!/usr/bin/env bash
# Instala a politica de eficiencia de tokens: no escopo de usuario (~/.claude) ou dentro de um projeto.
#
#   ./install.sh                      instala no escopo de USUARIO (~/.claude): vale para todos os
#                                     projetos desta maquina. NAO vale em sessoes em nuvem.
#   ./install.sh --project <pasta>    instala DENTRO de um repositorio (CLAUDE.md, .claude/settings.json,
#                                     .claude/hooks, .claude/skills). E o que vale em sessoes em nuvem
#                                     e para quem clona o repo. Depois, faca commit.
#   ./install.sh --dry-run [...]      mostra o que seria feito, sem alterar nada
#
# Nao instale os dois escopos no MESMO projeto na mesma maquina: o CLAUDE.md seria carregado duas vezes.
#
# Seguro para quem ja tem configuracao:
#   - backup de tudo que sera tocado em ~/.claude/backups-politica-tokens/<data>/
#   - settings.json e MESCLADO (listas unidas; valores que voce ja definiu NAO sao sobrescritos)
#   - CLAUDE.md recebe um bloco delimitado por marcadores; reexecutar substitui so esse bloco
#   - idempotente: rodar duas vezes nao duplica nada
# Requer: bash, jq
set -euo pipefail

DRY=0; PROJECT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --project) shift; PROJECT="${1:?--project exige uma pasta}" ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $1"; exit 2 ;;
  esac; shift
done
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/global" && pwd)"
if [ -n "$PROJECT" ]; then
  [ -d "$PROJECT" ] || { echo "erro: pasta nao existe: $PROJECT"; exit 1; }
  PROJECT="$(cd "$PROJECT" && pwd)"
  DEST="$PROJECT/.claude"; CM="$PROJECT/CLAUDE.md"
else
  DEST="${CLAUDE_HOME:-$HOME/.claude}"; CM="$DEST/CLAUDE.md"
fi
STAMP="$(date +%Y%m%d-%H%M%S)"
BK="$DEST/backups-politica-tokens/$STAMP"
START='<!-- politica-tokens:start -->'
END='<!-- politica-tokens:end -->'

command -v jq >/dev/null || { echo "erro: jq e necessario (apt install jq / brew install jq)"; exit 1; }
run() { if [ "$DRY" = 1 ]; then echo "[dry-run] $*"; else eval "$@"; fi; }
backup() { [ -e "$1" ] && run "mkdir -p '$BK' && cp -a '$1' '$BK/'" || true; }

echo "origem : $SRC"
echo "destino: $DEST   (dry-run=$DRY)"
run "mkdir -p '$DEST/hooks' '$DEST/skills'"

# 1) hooks -------------------------------------------------------------------
for f in quiet-run.sh rewrite-test-cmd.sh; do
  backup "$DEST/hooks/$f"
  run "cp '$SRC/hooks/$f' '$DEST/hooks/$f' && chmod +x '$DEST/hooks/$f'"
done

# 2) skills ------------------------------------------------------------------
for s in project-onboard context-audit; do
  backup "$DEST/skills/$s"
  run "rm -rf '$DEST/skills/$s' && cp -a '$SRC/skills/$s' '$DEST/skills/$s'"
done

# 3) CLAUDE.md global (bloco com marcadores) ---------------------------------
backup "$CM"
if [ "$DRY" = 1 ]; then
  echo "[dry-run] atualizar bloco politica-tokens em $CM"
else
  touch "$CM"
  # remove bloco antigo (se houver), preservando todo o resto do arquivo
  awk -v s="$START" -v e="$END" '
    $0==s {skip=1; next}
    $0==e {skip=0; next}
    !skip {print}' "$CM" | sed -e :a -e '/^\n*$/{$d;N;ba' -e '}' > "$CM.tmp"   # tira linhas vazias finais
  { cat "$CM.tmp"; [ -s "$CM.tmp" ] && echo; echo "$START"; cat "$SRC/CLAUDE.md"; echo "$END"; } > "$CM"
  rm -f "$CM.tmp"
fi

# 4) settings.json (merge) ---------------------------------------------------
ST="$DEST/settings.json"
backup "$ST"
SRC_SETTINGS="$SRC/settings.json"
if [ -n "$PROJECT" ]; then
  SRC_SETTINGS="$(mktemp)"
  jq '(.hooks.PreToolUse[].hooks[].command) |= sub("\\$HOME/\\.claude/hooks/"; "${CLAUDE_PROJECT_DIR}/.claude/hooks/")' "$SRC/settings.json" > "$SRC_SETTINGS"
fi
MERGE='
def merge($a; $b):
  if ($a|type)=="object" and ($b|type)=="object" then
    reduce ($b|keys_unsorted[]) as $k ($a; .[$k] = (if has($k) then merge(.[$k]; $b[$k]) else $b[$k] end))
  elif ($a|type)=="array" and ($b|type)=="array" then ($a + ($b - $a))   # uniao preservando a ordem do usuario
  elif $a == null then $b
  else $a end;                     # valor ja existente do usuario vence
merge(.[0]; .[1])'
if [ "$DRY" = 1 ]; then
  echo "[dry-run] mesclar $SRC/settings.json em $ST. Resultado seria:"
  if [ -s "$ST" ]; then jq -s "$MERGE" "$ST" "$SRC_SETTINGS"; else jq -s "$MERGE" <(echo '{}') "$SRC_SETTINGS"; fi
else
  if [ -s "$ST" ]; then
    jq -e . "$ST" >/dev/null || { echo "erro: $ST nao e JSON valido; nada foi alterado em settings."; exit 1; }
    if ! jq -s "$MERGE" "$ST" "$SRC_SETTINGS" > "$ST.tmp"; then
      rm -f "$ST.tmp"; echo "erro: falha ao mesclar settings.json; o arquivo original foi mantido."; exit 1
    fi
    jq -e . "$ST.tmp" >/dev/null && mv "$ST.tmp" "$ST"
  else
    jq -s "$MERGE" <(echo '{}') "$SRC_SETTINGS" > "$ST"     # mesma rota da mesclagem: saida identica desde a 1a execucao
  fi
fi

echo
echo "pronto. Verifique em uma sessao: /status (Setting sources), /hooks (PreToolUse), /skills."
[ "$DRY" = 1 ] || { [ -d "$BK" ] && echo "backup do que existia antes: $BK"; true; }
