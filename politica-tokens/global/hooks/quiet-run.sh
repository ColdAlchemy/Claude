#!/usr/bin/env bash
# quiet-run.sh - executa um comando de teste e devolve uma saida enxuta SEM perder informacao critica.
#
# Garantias (diferente de simplesmente fazer `| grep | head`):
#   1. O codigo de saida do comando original e preservado.
#   2. Saida curta (<= LIMITE linhas) passa inteira, sem alteracao.
#   3. Saida longa: mostra linhas de falha/erro, o rodape (onde runners imprimem o resumo)
#      e o caminho do log COMPLETO, que continua disponivel para leitura.
#   4. Se nada casar com o filtro de falhas, mostra so o rodape: "tudo passou" continua visivel.
#
# Uso: quiet-run.sh '<comando original>'
set -u
LIMITE="${QUIET_RUN_LIMIT:-150}"
cmd="${1:?comando ausente}"

log="$(mktemp "${TMPDIR:-/tmp}/quiet-run.XXXXXX.log")"
bash -c "$cmd" >"$log" 2>&1
rc=$?

linhas=$(wc -l <"$log" | tr -d ' ')
if [ "$linhas" -le "$LIMITE" ]; then
  cat "$log"
  rm -f "$log"
  exit "$rc"
fi

echo "[quiet-run] ${linhas} linhas de saida; exibindo falhas e rodape. Log completo: ${log}"
echo "[quiet-run] codigo de saida do comando: ${rc}"
echo "---- linhas com falha/erro (ate 80) ----"
grep -n -i -E 'fail|error|panic|traceback|exception|assert|✗|✖|FAILED' "$log" | head -80 || true
echo "---- ultimas 60 linhas ----"
tail -n 60 "$log"
exit "$rc"
