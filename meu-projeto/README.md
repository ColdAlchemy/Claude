# meu-projeto

Central de trabalho: tudo que é criado em sessões do Claude na nuvem
fica aqui, organizado, e chega ao seu PC por Git para abrir no
Antigravity.

## Como funciona

```text
Claude (nuvem)  ->  git push  ->  GitHub  ->  git pull  ->  seu PC (Antigravity)
```

1. Você descreve o que quer na conversa da nuvem.
2. O Claude cria ou altera arquivos aqui e envia (commit + push).
3. No seu PC você roda `git pull` e abre a pasta no Antigravity.

Passo a passo completo: [docs/fluxo-nuvem-pc.md](docs/fluxo-nuvem-pc.md)

## Estrutura

| Pasta / arquivo | Para que serve |
|---|---|
| `projetos/` | Um projeto por subpasta. Use `projetos/_modelo/` como ponto de partida. |
| `skills/` | Rascunhos das suas skills (ainda não ativas). Ver `skills/README.md`. |
| `docs/` | Guias e registros (fluxo nuvem -> PC, inventário de skills). |
| `scripts/` | Scripts de apoio para o seu PC (Windows/PowerShell). |
| `CLAUDE.md` | Regras que o Claude lê no início de cada sessão neste projeto. |

## Começar rápido

```powershell
git clone -b claude/peaceful-meitner-j086iy https://github.com/ColdAlchemy/Claude.git
cd Claude\meu-projeto
```

Depois, no Antigravity: **File -> Open Folder** e escolha `meu-projeto`.

## Criar um projeto novo

1. Copie `projetos/_modelo/` para `projetos/nome-do-projeto/`.
2. Preencha o `README.md` dele (objetivo, como rodar, status).
3. Peça ao Claude para trabalhar nessa pasta.
