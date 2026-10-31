# Contexto do trabalho (leia no início de uma sessão nova)

Resumo do que foi decidido e descoberto, para não precisar refazer.

## Objetivo do usuário
- Conversar pelo app Claude Desktop, em sessões na nuvem, e construir tudo
  na nuvem.
- Ver o resultado como pastas e arquivos no Antigravity IDE, no PC (Windows).
- Usar os **créditos de sessão na nuvem** (US$ 100, expiram em 05/11),
  não o plano Pro, cujo limite semanal estava em 100% (reinicia domingo 17:00).
- Preferência por interface gráfica; evita terminal.

## Como o trabalho chega ao PC
- Repositório: https://github.com/ColdAlchemy/Claude
- Branch de trabalho: `claude/peaceful-meitner-j086iy`
- Projeto: pasta `meu-projeto/` (o repositório também tem, na raiz, um
  relatório antigo de ativos dermatológicos, sem relação com isso).
- Clone no PC: `C:\Projetos\Nuvem\Claude\meu-projeto`
- Fluxo: Claude cria na nuvem, faz commit e push; no PC o script
  `scripts/sincronizar.ps1` roda `git pull --ff-only` a cada 15 s e as
  pastas aparecem no Antigravity. Detalhes em `docs/fluxo-nuvem-pc.md`.

## O que NÃO funciona (não tente de novo)
- Acesso direto da sessão na nuvem ao PC. O computador é `Orion` (Windows
  com WSL2/Ubuntu, usuário Windows `albrt`, usuário WSL `albert`).
  - A pasta do Windows é recusada pela plataforma (Windows nativo não é
    oferecido a sessões na nuvem).
  - O `claude remote-control` no WSL conecta, mas a pasta não entra na lista
    de pastas que a sessão na nuvem pode pedir.
- Criar sessão "dentro" do PC (`create_session` no ambiente do Orion): o
  modelo roda no PC e gasta o plano Pro, não os créditos da nuvem. Foi
  tentado uma vez, ficou parado em permissão e foi arquivado.

## Fatos importantes
- Sessões na nuvem consomem os créditos de sessão na nuvem; sessões locais
  consomem o plano. O Claude não vê esses saldos diretamente.
- Skills: 15 skills da conta claude.ai habilitadas e 16 embutidas. Lista e
  decisões pendentes em `docs/inventario-skills.md`. Skills locais do PC
  (`%USERPROFILE%\.claude\skills`) ainda não foram levantadas.
- A skill `image-prompt-generator` cita "Deborah", provavelmente herdada
  de outra pessoa.

## Pendências
1. Usuário decidir quais skills manter, remover ou criar.
2. Definir o primeiro projeto dentro de `projetos/` (usar `_modelo/`).
3. Opcional: levantar skills locais do PC pelo PowerShell.
4. Ao aprovar, juntar a branch à principal (nenhum PR foi aberto).
