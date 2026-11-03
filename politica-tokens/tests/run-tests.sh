#!/usr/bin/env bash
# Testes da politica: hooks e instalador. Nao toca no seu ~/.claude (usa diretorios temporarios).
#   ./tests/run-tests.sh
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$ROOT/global/hooks"
fail=0; n=0
ok(){ n=$((n+1)); echo "  OK     $1"; }
ko(){ n=$((n+1)); echo "  FALHOU $1"; fail=1; }
mk(){ mktemp -d; }

echo "== quiet-run.sh =="
out=$("$H/quiet-run.sh" 'echo ok; echo "3 passed"'); rc=$?
[ "$rc" = 0 ] && [ "$out" = $'ok\n3 passed' ] && ok "saida curta passa intacta, rc=0" || ko "saida curta"
"$H/quiet-run.sh" 'echo "FAILED test_x"; exit 3' >/dev/null; [ $? = 3 ] && ok "codigo de saida preservado (3)" || ko "rc"
out=$("$H/quiet-run.sh" 'for i in $(seq 1 250); do echo "t$i ok"; done; echo "FAIL: test_login assertion"; for i in $(seq 251 500); do echo "t$i ok"; done; echo "1 failed, 499 passed"; exit 1'); rc=$?
[ "$rc" = 1 ] && ok "rc=1 preservado em saida longa" || ko "rc longa"
echo "$out" | grep -q 'FAIL: test_login assertion' && ok "falha no meio de 500 linhas continua visivel" || ko "falha escondida"
echo "$out" | grep -q '1 failed, 499 passed' && ok "resumo final visivel" || ko "resumo"
echo "$out" | grep -q 'Log completo:' && ok "caminho do log completo informado" || ko "log"
out=$("$H/quiet-run.sh" 'for i in $(seq 1 300); do echo "t$i ok"; done; echo "300 passed in 2s"')
echo "$out" | grep -q '300 passed in 2s' && ok "'tudo passou' visivel quando nao ha falhas" || ko "tudo passou sumiu"

echo "== rewrite-test-cmd.sh =="
r(){ printf '{"tool_input":{"command":%s}}' "$(printf '%s' "$1" | jq -Rs .)" | "$H/rewrite-test-cmd.sh"; }
r 'pytest -x tests/' | jq -e '.hookSpecificOutput.updatedInput.command | contains("quiet-run.sh")' >/dev/null && ok "pytest e reescrito" || ko "pytest"
for c in 'pytest | tee out.txt' 'git status' 'pytest; rm -rf /tmp/x' 'npm test && npm run deploy' 'pytest $(whoami)' 'ls > pytest'; do
  [ "$(r "$c")" = '{}' ] && ok "intacto: $c" || ko "reescreveu indevidamente: $c"
done
nc=$(r 'pytest -k "a and b"' | jq -r '.hookSpecificOutput.updatedInput.command')
out=$(cd "$(mk)" && printf 'def test_a_and_b():\n    assert True\n' > test_x.py && eval "$nc" 2>&1)
echo "$out" | grep -q '1 passed' && ok "comando com aspas executa ponta a ponta" || ko "aspas: $out"

echo "== install.sh =="
S="$ROOT/install.sh"
export CLAUDE_HOME="$(mk)/.claude"; "$S" >/dev/null 2>"$CLAUDE_HOME.err" || ko "instalacao limpa falhou"
[ "$(jq '.permissions.deny|length' "$CLAUDE_HOME/settings.json")" = 5 ] && ok "limpa: 5 regras deny" || ko "limpa: deny"
[ -x "$CLAUDE_HOME/hooks/quiet-run.sh" ] && [ -f "$CLAUDE_HOME/skills/context-audit/SKILL.md" ] && ok "limpa: hooks e skills copiados" || ko "limpa: copia"

export CLAUDE_HOME="$(mk)/.claude"; mkdir -p "$CLAUDE_HOME"
cat > "$CLAUDE_HOME/settings.json" <<'EOF'
{"model":"claude-opus-5-5","permissions":{"allow":["Bash(npm run lint)"],"deny":["Read(./.env)","Read(./dist/**)"]},
 "env":{"CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION":"true","FOO":"bar"},
 "hooks":{"PreToolUse":[{"matcher":"Edit","hooks":[{"type":"command","command":"meu-hook.sh"}]}]}}
EOF
printf '# Minhas regras\n- responda em pt-BR\n' > "$CLAUDE_HOME/CLAUDE.md"
"$S" >/dev/null 2>"$CLAUDE_HOME.err" && ok "existente: instalou" || ko "existente: falhou"
[ ! -s "$CLAUDE_HOME.err" ] && ok "existente: sem erro silencioso" || ko "existente: stderr=$(cat "$CLAUDE_HOME.err")"
T="$CLAUDE_HOME/settings.json"
[ "$(jq -r .model "$T")" = claude-opus-5-5 ] && ok "existente: model preservado" || ko model
[ "$(jq -r .env.CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION "$T")" = true ] && ok "existente: valor do usuario NAO sobrescrito" || ko "sobrescreveu"
[ "$(jq -r .env.FOO "$T")" = bar ] && [ "$(jq -r .env.CLAUDE_CODE_ENABLE_AWAY_SUMMARY "$T")" = 0 ] && ok "existente: env mesclado" || ko env
[ "$(jq '.permissions.allow|length' "$T")" = 1 ] && ok "existente: allow intacto" || ko allow
[ "$(jq '.permissions.deny|length' "$T")" = 6 ] && ok "existente: deny unido sem duplicar (2+5-1=6)" || ko "deny=$(jq '.permissions.deny|length' "$T")"
[ "$(jq -r '[.hooks.PreToolUse[].matcher]|sort|join(",")' "$T")" = "Bash,Edit" ] && ok "existente: hook do usuario mantido + Bash adicionado" || ko hooks
head -2 "$CLAUDE_HOME/CLAUDE.md" | grep -q 'Minhas regras' && ok "existente: texto do usuario no CLAUDE.md preservado" || ko claudemd
ls "$CLAUDE_HOME"/backups-politica-tokens/*/settings.json >/dev/null 2>&1 && ok "existente: backup criado" || ko backup
cp "$T" /tmp/pt-s1.json; cp "$CLAUDE_HOME/CLAUDE.md" /tmp/pt-c1.md
"$S" >/dev/null 2>&1; "$S" >/dev/null 2>&1
diff <(jq -S . /tmp/pt-s1.json) <(jq -S . "$T") >/dev/null && ok "idempotente: settings" || ko "idempotencia settings"
diff /tmp/pt-c1.md "$CLAUDE_HOME/CLAUDE.md" >/dev/null && ok "idempotente: CLAUDE.md" || ko "idempotencia CLAUDE.md"

export CLAUDE_HOME="$(mk)/.claude"; "$S" --dry-run >/dev/null 2>&1; [ ! -e "$CLAUDE_HOME" ] && ok "dry-run nao cria nada" || ko "dry-run"
export CLAUDE_HOME="$(mk)/.claude"; mkdir -p "$CLAUDE_HOME"; echo '{ quebrado' > "$CLAUDE_HOME/settings.json"
"$S" >/dev/null 2>&1 && ko "deveria abortar com JSON invalido" || ok "JSON invalido: aborta"
[ "$(cat "$CLAUDE_HOME/settings.json")" = '{ quebrado' ] && ok "JSON invalido: original intacto" || ko "original alterado"

echo "== install.sh (escopo de usuario: comando do hook) =="
export CLAUDE_HOME="$(mk)/.claude"; "$S" >/dev/null 2>&1
cmd=$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$CLAUDE_HOME/settings.json")
out=$(HOME="$(dirname "$CLAUDE_HOME")" sh -c "printf '%s' '{\"tool_input\":{\"command\":\"pytest -x\"}}' | $cmd" 2>&1)
echo "$out" | jq -e '.hookSpecificOutput.updatedInput.command | contains("quiet-run.sh")' >/dev/null 2>&1 \
  && ok "comando do hook (\$HOME) executa via sh e reescreve pytest" || ko "hook \$HOME: $out"

echo "== install.sh --project =="
export CLAUDE_HOME="$(mk)/.claude-nao-deve-ser-tocado"
PD="$(mk)/meu projeto"; mkdir -p "$PD"; printf '# Meu projeto\n- npm test\n' > "$PD/CLAUDE.md"
"$S" --project "$PD" >/dev/null 2>"$PD.err" && ok "projeto: instalou" || ko "projeto: falhou"
[ ! -s "$PD.err" ] && ok "projeto: sem erro" || ko "projeto stderr: $(cat "$PD.err")"
[ ! -e "$CLAUDE_HOME" ] && ok "projeto: nao tocou no escopo de usuario" || ko "projeto tocou no escopo de usuario"
head -2 "$PD/CLAUDE.md" | grep -q 'Meu projeto' && grep -q 'politica-tokens:start' "$PD/CLAUDE.md" && ok "projeto: CLAUDE.md do projeto preservado + bloco" || ko "projeto: CLAUDE.md"
pc=$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$PD/.claude/settings.json")
case "$pc" in *CLAUDE_PROJECT_DIR*) ok "projeto: hook usa \${CLAUDE_PROJECT_DIR}";; *) ko "projeto: hook sem CLAUDE_PROJECT_DIR: $pc";; esac
out=$(CLAUDE_PROJECT_DIR="$PD" sh -c "printf '%s' '{\"tool_input\":{\"command\":\"pytest\"}}' | $pc" 2>&1)
echo "$out" | jq -e '.hookSpecificOutput.updatedInput.command | contains("quiet-run.sh")' >/dev/null 2>&1 \
  && ok "projeto: hook executa mesmo com espaco no caminho" || ko "projeto hook exec: $out"
[ -x "$PD/.claude/hooks/quiet-run.sh" ] && [ -f "$PD/.claude/skills/project-onboard/SKILL.md" ] && ok "projeto: hooks e skills dentro do repo" || ko "projeto: copia"
cp "$PD/CLAUDE.md" /tmp/pt-pc1.md; cp "$PD/.claude/settings.json" /tmp/pt-ps1.json
"$S" --project "$PD" >/dev/null 2>&1
diff /tmp/pt-pc1.md "$PD/CLAUDE.md" >/dev/null && diff <(jq -S . /tmp/pt-ps1.json) <(jq -S . "$PD/.claude/settings.json") >/dev/null && ok "projeto: idempotente" || ko "projeto: idempotencia"
"$S" --project /nao/existe >/dev/null 2>&1 && ko "pasta inexistente deveria falhar" || ok "projeto: pasta inexistente aborta"

echo; echo "$n verificacoes."; [ $fail = 0 ] && echo "TODAS PASSARAM" || { echo "HA FALHAS"; exit 1; }
