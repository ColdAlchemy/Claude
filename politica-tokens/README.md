# Política de eficiência de tokens para o Claude Code

Conjunto instalável que reduz gasto de tokens em **qualquer projeto**, antigo ou novo, sem trocar
rigor por economia. Tudo aqui foi conferido na documentação oficial (code.claude.com, consultada em
2026-11-03) e o que executa código foi testado.

> **Honestidade sobre o alcance.** Isto não prova que "nenhuma qualidade é perdida" nem é "irrefutável".
> Cada peça abaixo traz seu risco declarado. As que não têm troca real de qualidade estão ativas por
> padrão. As que têm ficaram **de fora do padrão** e viraram decisão sua (seção 4).

## 1. Instalar

Escolha **onde** você usa o Claude Code. Isso decide o escopo, e o erro mais fácil é usar o errado:

| Você usa | Instale com | Por quê |
|---|---|---|
| Terminal / IDE / desktop **local** | `./install.sh` | Vai para `~/.claude`; vale para todos os projetos da máquina |
| **Sessões em nuvem** (claude.ai/code, app) | `./install.sh --project <pasta-do-repo>` e faça commit | Segundo a documentação, sessões em nuvem **não leem** `~/.claude` (nem settings, nem skills pessoais). Só vale o que está no repositório |

```bash
./install.sh --dry-run                   # só mostra o que faria
./install.sh                             # escopo de usuário
./install.sh --project ~/code/meu-app    # dentro de um repositório
./tests/run-tests.sh                     # 42 verificações (não toca no seu ~/.claude)
```

O instalador faz backup, **mescla** o `settings.json` (nunca sobrescreve um valor que você já definiu), mantém o
resto do seu `CLAUDE.md`, e é idempotente. Não instale os dois escopos no mesmo projeto na mesma máquina: o
`CLAUDE.md` seria carregado duas vezes. Requer `bash` e `jq`.

## 2. O que cada peça faz

| Peça | Efeito | Base | Risco para a qualidade |
|---|---|---|---|
| `CLAUDE.md` global (~400 palavras) | Busca específica, plano antes de mudança ampla, verificar antes de dizer "pronto", resposta final curta, instruções de compactação | Costs + Best practices: "só o que o Claude não infere do código"; abaixo de ~200 linhas | Nenhum esperado. Exige verificação, não a dispensa |
| Hook `rewrite-test-cmd.sh` + `quiet-run.sh` | Saída longa de testes vira falhas + rodapé; log completo fica em arquivo | Costs: hooks podem pré-processar saída | Baixo. Preserva código de saída, mantém falhas e "tudo passou" visíveis (testado) |
| `permissions.deny` em `dist/`, `.next/`, `coverage/`, `*.min.js`, `*.map` | Evita leituras acidentais de arquivos gerados | Settings/permissions | Baixo, **mas bloqueia também o `cat` via Bash** (testado). Se precisar ler um desses, remova a regra |
| `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false`, `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=0` | Corta requisições de fundo (sugestão de próximo prompt, resumo ao voltar) | Costs, "Background token usage" | Nenhum na qualidade. Você perde essas duas conveniências |
| Skill `/project-onboard` | Descobre e **verifica** comandos e armadilhas uma vez; propõe `CLAUDE.md` curto | Costs: skill de visão geral evita exploração repetida; Best practices: registrar só o não inferível | Nenhum. Pede confirmação antes de gravar |
| Skill `/context-audit` | Mede o contexto fixo do projeto e propõe cortes | Costs: mover instruções do `CLAUDE.md` para skills | Nenhum. Só lê e propõe |
| `tools/cc_diagnose.py` | Mostra onde seus tokens foram, por projeto, sessão e ferramenta | — | Nenhum (somente leitura) |

As duas skills usam `disable-model-invocation: true`: segundo a documentação, assim nem a descrição ocupa contexto.

## 3. O que foi testado e o que não foi

**Testado (reproduzível com `./tests/run-tests.sh`, 42 verificações):** wrapper de saída (código de saída, falha no
meio de 500 linhas, "tudo passou"), padrão do hook (não reescreve pipelines nem `;`/`&&`/`$()`), instalador
(instalação limpa, mesclagem com conflito, idempotência, dry-run, JSON inválido, modo projeto, caminho com espaço).
O teste achou e eu corrigi três defeitos meus no instalador antes de entregar.

**Testado no Claude Code de verdade** (`claude -p`, projeto sintético: 400 testes, 1 falhando):

| | sem hook (n=4) | com hook (n=4) |
|---|---|---|
| Acertou o teste que falha | 4/4 | 4/4 |
| Turnos | 3 | 2 |
| Custo médio | US$ 0,072 | US$ 0,051 (≈ −30%) |

Sem o hook, o Claude Code truncou a saída, a falha não apareceu e o modelo rodou o comando de novo. Também
confirmei em sessão real que o `deny` bloqueia `Read` e `Bash cat`, que a skill `/project-onboard` executa,
verifica comandos e pede confirmação, e que o hook instalado em modo projeto dispara via `${CLAUDE_PROJECT_DIR}`.

**Não validado, e você deve saber:**
- O ganho de ≈30% vale para **esse cenário**: um projeto sintético, um tipo de tarefa, uma saída de teste bem
  verbosa. Em projetos reais pode ser menor. Não é uma estimativa geral.
- Não medi o efeito do `CLAUDE.md` global na qualidade em tarefas reais e variadas. Ele segue o que a
  documentação recomenda, e os runs mostraram o modelo seguindo-o (filtrou saída e preservou o código de saída),
  mas isso não é um estudo de qualidade.
- Não testei em Windows nativo (o instalador exige `bash` e `jq`), nem o hook com runners de teste fora da lista do padrão.
- O `quiet-run` mantém o log completo em `/tmp`; em sistemas que limpam `/tmp` rápido, o log some.

## 4. Decisões suas (alavancas fora do padrão, porque têm troca real)

A documentação indica que o maior ganho está aqui, e é onde "sem perder qualidade" é de fato uma pergunta aberta.
Eu não as ativei por você, e não medi o impacto na qualidade.

| Alavanca | Como | O que se sabe |
|---|---|---|
| **Modelo** | `/model` | Docs: Sonnet cobre a maior parte das tarefas por menos que Opus; reservar o mais forte para arquitetura e raciocínio em várias etapas. Trocar de modelo no meio da sessão reconstrói o cache |
| **Esforço de raciocínio** | `/effort` | Docs: pensar custa tokens de saída. Reduzir para tarefas simples. Não dá para desligar o raciocínio nos modelos 5.x |
| **Subagentes** | — | Docs: **não** economizam tokens totais; só tiram saída ruidosa da conversa. Haiku nos de busca simples |
| **Compactação antecipada** | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Só reduz o limiar. Resume mais cedo: economiza, mas pode perder detalhe. Em nuvem, a variável já é definida pela plataforma |
| **Limite de saída do Bash** | `BASH_MAX_OUTPUT_LENGTH` (padrão 30000) | Reduzir corta ruído, mas pode truncar informação útil |
| **Deny em lockfiles/`node_modules`** | `permissions.deny` | **Não recomendo**: bloqueia leitura legítima (depurar uma dependência), e o ganho é incerto: acredito que a busca já ignore o que está no `.gitignore`, mas **não verifiquei** |

## 5. Hábitos que nenhuma configuração faz por você (os de maior efeito)

Todos documentados em Costs / Best practices:
1. `/clear` entre tarefas não relacionadas (custa zero). O contexto antigo é reenviado a cada mensagem.
2. Pedidos específicos ("valide o login em `auth.ts`"), não "melhore o projeto".
3. Dar o critério de pronto ("rode `npm test` e me mostre passando"). Evita retrabalho, o maior desperdício.
4. Plan mode (Shift+Tab) antes de mudanças grandes; Esc cedo; depois de duas correções falhas, `/clear` com prompt melhor.
5. Desligar servidores MCP e plugins sem uso (`/mcp`); preferir CLI (`gh`, `aws`…) a MCP quando existir.

## 6. Como medir o resultado nos seus projetos

Em vez de confiar em benchmark genérico, compare antes e depois, nos seus projetos:
- `/usage` (planos Pro/Max/Team): atribuição por skill, subagente, plugin e MCP, com recomendações oficiais. `/context` mostra o que ocupa a janela. `/insights` analisa padrões de uso.
- `python3 tools/cc_diagnose.py --dias 30`: complementa o `/usage` (ferramentas que mais enchem o contexto, arquivos relidos, sessões antigas). O custo que ele mostra é **relativo** (pesos de mercado), não a sua fatura.

## 7. Manutenção

O Claude Code muda rápido (esta política foi conferida contra a versão 2.1.317). Rode `./tests/run-tests.sh`
depois de qualquer alteração aqui, e reconfira as fontes ao atualizar o CLI:
[costs](https://code.claude.com/docs/en/costs) · [best-practices](https://code.claude.com/docs/en/best-practices) ·
[settings](https://code.claude.com/docs/en/settings) · [skills](https://code.claude.com/docs/en/skills) ·
[hooks](https://code.claude.com/docs/en/hooks) · [cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web).
