# skills/

Área de rascunho das suas skills. Nada aqui está ativo ainda.

## Como virar skill ativa
Uma skill é uma pasta com um `SKILL.md`:

```text
nome-da-skill/
  SKILL.md
```

No topo do `SKILL.md` vão `name` e `description`, que dizem ao Claude
quando usar a skill:

```markdown
---
name: nome-da-skill
description: Quando usar esta skill, em uma ou duas frases.
---

Instruções para o Claude.
```

Para valer em sessões na nuvem de um repositório, a pasta precisa ficar em
`.claude/skills/` na **raiz do repositório** onde a sessão roda. Para valer
só no seu PC, em `%USERPROFILE%\.claude\skills\`.

Decida primeiro quais manter ou remover em `docs/inventario-skills.md`.
