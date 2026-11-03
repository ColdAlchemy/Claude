---
name: project-onboard
description: Prepara um projeto (novo ou legado) para sessões eficientes, criando ou enxugando o CLAUDE.md do projeto com comandos verificados e armadilhas reais. Invocar manualmente com /project-onboard.
disable-model-invocation: true
---

# Onboarding de projeto

Objetivo: pagar UMA vez o custo de descobrir como o projeto funciona e deixar isso registrado,
para que as próximas sessões não repitam a exploração. Registre só o que NÃO dá para inferir
lendo o código. Não descreva a estrutura de pastas nem a arquitetura: o Claude lê o repositório.

## Passos

1. **Estado atual.** Verifique se já existe `CLAUDE.md` (raiz e subpastas), `.claude/` e
   README. Se existir CLAUDE.md, leia-o inteiro: a tarefa passa a ser enxugar e corrigir, não
   reescrever do zero. Nunca sobrescreva sem mostrar o diff e pedir confirmação.

2. **Descobrir comandos** nos manifestos (package.json, Makefile, pyproject.toml, Cargo.toml,
   go.mod, pom.xml, build.gradle, docker-compose, CI em .github/workflows etc.). O CI costuma ser a
   fonte mais confiável do que realmente precisa passar.

3. **Verificar de verdade.** Rode os comandos de instalar, testar, lint, tipos e build (com
   saída filtrada: `tail`, flags quietas). Registre só o que funcionou. Se algo falhar, anote o
   comando que funciona de fato ou a causa (ex.: precisa de serviço X, variável Y, versão Z).
   Não invente comandos que você não executou.

4. **Caçar armadilhas.** Procure o que costuma custar caro a quem chega sem contexto: testes
   lentos ou flaky, ordem obrigatória de comandos, arquivos gerados que não se edita, convenções
   que contrariam o padrão da linguagem, variáveis de ambiente exigidas, diretórios que nunca
   devem ser tocados. Inclua apenas o que tem evidência (arquivo, CI, README ou execução).

5. **Escrever `CLAUDE.md`** com no máximo ~60 linhas, nesta ordem:
   - Comandos (instalar, rodar um teste isolado, suíte, lint, tipos, build, dev server).
   - Armadilhas e regras que o código não revela.
   - Convenções que diferem do padrão.
   - Como verificar que uma mudança está pronta.
   Cada linha deve passar no teste: "o Claude erraria sem isso?". Se não, remova.

6. **Sugerir, sem aplicar:** diretórios gerados do projeto para `permissions.deny` no
   `.claude/settings.json` do projeto, e instruções longas e específicas de um fluxo que
   deveriam virar skill do projeto em vez de ficar no CLAUDE.md.

## Saída final
Mostre o CLAUDE.md proposto (ou o diff), liste o que foi verificado por execução e o que ficou
sem verificação, e pergunte antes de gravar.
