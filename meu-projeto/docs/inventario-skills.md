# Inventário de skills

Levantamento feito na sessão em nuvem. Preencha a coluna **Decisão** com
`manter`, `remover` ou `rever`.

> Só aparecem skills visíveis na sessão em nuvem: as da conta claude.ai
> habilitadas e as embutidas. Skills locais do seu PC (`~/.claude/skills`)
> e plugins instalados localmente ainda não foram levantados.

## Skills da conta claude.ai (15, todas habilitadas)

| Skill | Para que serve | Decisão |
|---|---|---|
| docs | Documentos editáveis e compartilháveis | |
| docx | Arquivos Word (.docx/.dotx) | |
| xlsx | Planilhas (.xlsx, .csv, .tsv) | |
| pptx | PowerPoint (.pptx/.potx) | |
| pdf | Ler, juntar, dividir, preencher, criar e OCR de PDF | |
| google-workspace | Criar ou editar Google Docs, Sheets e Slides | |
| deep-research | Pesquisa em várias fontes com relatório narrativo | |
| skill-creator | Criar, melhorar e testar skills | |
| image-prompt-generator | Prompts para imagens (GPT Image). Descrição cita "Deborah" | rever |
| morning | Resumo matinal em HTML ou tarefa recorrente | |
| import-memory | Importar memória de outro assistente de IA | |
| artifact-emulator | Ver como um artifact aparece (screenshot) | |
| computer-use | Controlar apps do computador (app desktop) | |
| chrome-browser | Claude no Chrome | |
| built-in-browser | Navegador embutido do app desktop | |

## Skills embutidas do Claude Code (não removíveis)

session-start-hook, dataviz, artifact-design, artifact-diagramming,
artifact-capabilities, update-config, keybindings-help, code-review,
simplify, fewer-permission-prompts, loop, claude-api, run,
plugin-authoring, init, security-review.

## Observações

- Sobreposição: `docs`, `docx` e `google-workspace` cobrem partes
  parecidas. O mesmo vale para `chrome-browser`, `built-in-browser` e
  `computer-use`, que dependem do app desktop ou de um computador conectado.
- Nenhum plugin ativo na conta.
- As skills da conta são gerenciadas em claude.ai (Settings ->
  Capabilities). Daqui não é possível desativá-las.

## Pendente

Levantar no PC (PowerShell) e anotar aqui:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\skills" -ErrorAction SilentlyContinue | Select-Object Name
```

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\plugins" -ErrorAction SilentlyContinue | Select-Object Name
```
