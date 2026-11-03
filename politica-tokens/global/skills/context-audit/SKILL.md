---
name: context-audit
description: Audita o que o projeto atual carrega de contexto fixo (CLAUDE.md, skills, configurações, saídas e diretórios volumosos) e propõe cortes sem perda de qualidade. Invocar manualmente com /context-audit.
disable-model-invocation: true
---

# Auditoria de contexto fixo

Contexto fixo é o que é enviado em toda requisição da sessão. Cada linha desnecessária é paga
a cada turno. Esta auditoria só LÊ e PROPÕE; não altera nada sem aprovação.

## O que medir (use comandos, não estimativas)

1. **CLAUDE.md**: `wc -l` e tamanho em caracteres de `~/.claude/CLAUDE.md`, `./CLAUDE.md`,
   `./CLAUDE.local.md` e CLAUDE.md em subpastas (`find . -name CLAUDE.md -not -path '*/node_modules/*'`).
   Meta documentada: manter abaixo de ~200 linhas; aqui, o ideal é abaixo de 100.
2. **Skills**: liste `~/.claude/skills/*/SKILL.md` e `.claude/skills/*/SKILL.md`. Para cada uma,
   anote o tamanho do corpo e se a `description` é específica (diz QUANDO usar). Skills que só
   você dispara devem ter `disable-model-invocation: true`. Corpo acima de ~500 linhas deve mover
   o detalhe para arquivos de apoio.
3. **Configurações**: leia `~/.claude/settings.json`, `.claude/settings.json` e
   `.claude/settings.local.json`. Confira se diretórios gerados e volumosos do projeto estão em
   `permissions.deny` e se há hooks de filtro de saída.
4. **Volumes ocultos**: procure no projeto diretórios gerados ou grandes que a busca poderia
   atingir (`du -sh */ | sort -h | tail`), arquivos minificados, lockfiles gigantes, dumps e logs
   versionados.

## Como julgar cada item de CLAUDE.md
Pergunta única: "o Claude erraria ou gastaria muito para descobrir isso sozinho?"
- Não → remover (estrutura de pastas, descrição de arquitetura, convenções óbvias da linguagem).
- Sim, mas só em um fluxo específico → mover para uma skill do projeto.
- Regra sem exceção (ex.: nunca editar `migrations/`) → candidata a hook ou `deny`, não a texto.
- Sim e vale para toda tarefa → manter, em uma linha.

## O que você NÃO consegue ver
Você não executa `/context`, `/usage` nem `/mcp` (são comandos do usuário). Termine a
auditoria pedindo ao usuário que rode `/usage` (atribuição por skill, subagente, plugin e MCP, com
recomendações) e `/context`, e que desative servidores MCP sem uso com `/mcp`.

## Saída
Tabela: item | tamanho | problema | ação proposta | risco para a qualidade (nenhum/baixo/médio).
Ordene pelo maior ganho. Pergunte quais ações aplicar.
