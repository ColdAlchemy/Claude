#!/usr/bin/env python3
"""
cc_diagnose.py - onde seus tokens do Claude Code estao indo?

Le as transcricoes locais (~/.claude/projects/*/*.jsonl) e mostra, por projeto:
  - tokens por categoria (entrada nova, escrita de cache, leitura de cache, saida)
  - custo relativo estimado (pesos configuraveis, ver --pesos)
  - sessoes mais caras e quanto o contexto cresceu nelas
  - ferramentas que mais enchem o contexto (tamanho dos resultados)
  - arquivos lidos repetidamente na mesma sessao
  - uso por modelo e parcela de subagentes

Somente leitura. Nada e enviado a lugar nenhum.

Uso:
  python3 cc_diagnose.py                      # todos os projetos
  python3 cc_diagnose.py --projeto meu-app    # filtra por trecho do nome da pasta
  python3 cc_diagnose.py --dias 30 --top 10
"""
import argparse, json, os, glob, collections, time
from datetime import datetime, timezone

# Pesos RELATIVOS por categoria (preco/entrada-normal). Valores tipicos de
# mercado: leitura de cache ~0.1x, escrita de cache ~1.25x (5min) ou ~2x (1h),
# saida ~5x. Ajuste com --pesos se os precos do seu modelo forem diferentes.
PESOS_PADRAO = dict(input=1.0, cache_write=1.25, cache_read=0.1, output=5.0)


def parse_ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0


def tamanho_conteudo(c):
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        n = 0
        for b in c:
            if isinstance(b, dict):
                n += len(b.get("text", "")) if b.get("type") == "text" else len(json.dumps(b))
            else:
                n += len(str(b))
        return n
    return len(json.dumps(c)) if c else 0


def analisa_sessao(path, desde):
    msgs = {}  # message.id -> (usage, model, sidechain, ts)
    tool_uso = {}  # tool_use_id -> (nome, entrada)
    resultados = collections.defaultdict(lambda: [0, 0])  # nome -> [n, chars]
    maiores = []  # (chars, nome, resumo)
    leituras = collections.Counter()
    turnos_ctx = []
    ts_min = ts_max = 0
    for linha in open(path, errors="replace"):
        try:
            d = json.loads(linha)
        except Exception:
            continue
        ts = parse_ts(d.get("timestamp", ""))
        if ts:
            ts_min = ts if not ts_min else min(ts_min, ts)
            ts_max = max(ts_max, ts)
        t = d.get("type")
        m = d.get("message") or {}
        if t == "assistant" and isinstance(m, dict):
            u = m.get("usage")
            if u:
                # varias linhas por mesma resposta: guarda a ultima por id
                msgs[m.get("id") or d.get("uuid")] = (u, m.get("model", "?"), bool(d.get("isSidechain")), ts)
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tool_uso[b["id"]] = (b.get("name", "?"), b.get("input") or {})
                    if b.get("name") == "Read":
                        fp = (b.get("input") or {}).get("file_path")
                        if fp:
                            leituras[fp] += 1
        elif t == "user" and isinstance(m, dict):
            c = m.get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        nome, inp = tool_uso.get(b.get("tool_use_id"), ("?", {}))
                        n = tamanho_conteudo(b.get("content"))
                        resultados[nome][0] += 1
                        resultados[nome][1] += n
                        resumo = inp.get("file_path") or inp.get("command") or inp.get("pattern") or inp.get("description") or ""
                        maiores.append((n, nome, str(resumo)[:90]))
    if desde and ts_max and ts_max < desde:
        return None
    tot = collections.Counter()
    por_modelo = collections.defaultdict(collections.Counter)
    sub = collections.Counter()
    for u, modelo, side, ts in msgs.values():
        i = u.get("input_tokens", 0)
        cw = u.get("cache_creation_input_tokens", 0)
        cr = u.get("cache_read_input_tokens", 0)
        o = u.get("output_tokens", 0)
        for k, v in (("input", i), ("cache_write", cw), ("cache_read", cr), ("output", o)):
            tot[k] += v
            por_modelo[modelo][k] += v
            if side:
                sub[k] += v
        turnos_ctx.append(i + cw + cr)
    return dict(
        path=path, turnos=len(msgs), tot=tot, por_modelo=por_modelo, sub=sub,
        resultados=resultados, maiores=sorted(maiores, reverse=True)[:5],
        repetidas={k: v for k, v in leituras.items() if v >= 3},
        ctx_ini=turnos_ctx[0] if turnos_ctx else 0,
        ctx_fim=turnos_ctx[-1] if turnos_ctx else 0,
        ctx_max=max(turnos_ctx) if turnos_ctx else 0,
        ts_max=ts_max, dur=(ts_max - ts_min) if ts_min else 0,
    )


def custo(tot, p):
    return sum(tot.get(k, 0) * p[k] for k in p)


def fmt(n):
    return f"{n/1e6:.2f}M" if n >= 1e6 else f"{n/1e3:.1f}k" if n >= 1e3 else str(int(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--projeto", default="")
    ap.add_argument("--dias", type=int, default=0, help="so sessoes ativas nos ultimos N dias")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--pesos", default="", help="ex: input=1,cache_write=1.25,cache_read=0.1,output=5")
    a = ap.parse_args()
    p = dict(PESOS_PADRAO)
    for kv in filter(None, a.pesos.split(",")):
        k, v = kv.split("=")
        p[k.strip()] = float(v)
    desde = time.time() - a.dias * 86400 if a.dias else 0

    projetos = collections.defaultdict(list)
    for d in sorted(glob.glob(os.path.join(a.raiz, "*"))):
        if a.projeto and a.projeto not in os.path.basename(d):
            continue
        for f in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True):
            r = analisa_sessao(f, desde)
            if r and r["turnos"]:
                projetos[os.path.basename(d)].append(r)
    if not projetos:
        print("Nenhuma sessao encontrada em", a.raiz)
        return

    resumo = []
    for nome, ss in projetos.items():
        tot = collections.Counter()
        for s in ss:
            tot.update(s["tot"])
        resumo.append((custo(tot, p), nome, ss, tot))
    resumo.sort(reverse=True)
    total_geral = sum(r[0] for r in resumo) or 1

    print("=" * 72)
    print("PROJETOS por custo relativo (pesos:", p, ")")
    print("=" * 72)
    for c, nome, ss, tot in resumo:
        print(f"{c/total_geral*100:5.1f}%  {nome}  | sessoes={len(ss)}  turnos={sum(s['turnos'] for s in ss)}")

    for c, nome, ss, tot in resumo[: a.top]:
        print("\n" + "=" * 72)
        print(f"PROJETO: {nome}  ({c/total_geral*100:.1f}% do total)")
        print("=" * 72)
        tc = custo(tot, p) or 1
        print("Onde o custo relativo se concentra:")
        for k in ("input", "cache_write", "cache_read", "output"):
            print(f"  {k:12s} {fmt(tot[k]):>9s} tokens  -> {tot[k]*p[k]/tc*100:5.1f}% do custo")
        sub_c = custo(collections.Counter(sum((s['sub'] for s in ss), collections.Counter())), p)
        print(f"  subagentes: {sub_c/tc*100:.1f}% do custo")

        modelos = collections.defaultdict(collections.Counter)
        for s in ss:
            for m, cnt in s["por_modelo"].items():
                modelos[m].update(cnt)
        print("Por modelo:")
        for m, cnt in sorted(modelos.items(), key=lambda x: -custo(x[1], p)):
            print(f"  {m:28s} {custo(cnt,p)/tc*100:5.1f}% do custo")

        print(f"Sessoes mais caras (top {a.top}):")
        for s in sorted(ss, key=lambda s: -custo(s["tot"], p))[: a.top]:
            dur = f"{s['dur']/3600:.1f}h"
            print(f"  {os.path.basename(s['path'])[:12]}  custo={custo(s['tot'],p)/tc*100:5.1f}%  turnos={s['turnos']:4d}  "
                  f"contexto {fmt(s['ctx_ini'])} -> {fmt(s['ctx_fim'])} (max {fmt(s['ctx_max'])})  dur={dur}")

        agg = collections.defaultdict(lambda: [0, 0])
        grandes = []
        rep = collections.Counter()
        for s in ss:
            for k, (n, ch) in s["resultados"].items():
                agg[k][0] += n
                agg[k][1] += ch
            grandes += s["maiores"]
            rep.update(s["repetidas"])
        print("Ferramentas que mais devolvem texto ao contexto (aprox. 1 token ~ 4 chars):")
        for k, (n, ch) in sorted(agg.items(), key=lambda x: -x[1][1])[:6]:
            print(f"  {k:14s} {n:5d} chamadas  ~{fmt(ch/4)} tokens  (media {fmt(ch/4/max(n,1))}/chamada)")
        print("Maiores resultados individuais:")
        for ch, k, r in sorted(grandes, reverse=True)[:5]:
            print(f"  ~{fmt(ch/4):>7s} tokens  {k}: {r}")
        if rep:
            print("Arquivos lidos 3+ vezes na mesma sessao:")
            for fp, n in rep.most_common(5):
                print(f"  {n}x  {fp}")

    print("\nLeitura rapida:")
    print(" - cache_read alto e normal; o que pesa e contexto grande x muitos turnos.")
    print(" - contexto crescendo muito dentro de uma sessao => /clear ou /compact antes.")
    print(" - uma ferramenta com media alta por chamada => filtrar saida ou apontar arquivo/linha.")
    print(" - o custo e RELATIVO (pesos de mercado), nao a sua fatura; ajuste com --pesos.")


if __name__ == "__main__":
    main()
