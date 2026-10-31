# CLAUDE.md

Instruções para o Claude ao trabalhar em `meu-projeto/`.

## Contexto
- O usuário trabalha em Windows, com o Antigravity IDE e terminal PowerShell.
- Sessões na nuvem criam os arquivos; o usuário os recebe por `git pull`.
- Você não tem acesso direto ao PC do usuário. Comandos que precisam rodar
  lá devem ser entregues prontos, um bloco de código por comando.

Leia também `docs/contexto.md`: decisões já tomadas, o que não funciona e
as pendências atuais.

## Idioma e tom
- Responda em português do Brasil, de forma direta e objetiva.
- Explique passos de forma específica (onde clicar, o que digitar) quando
  o usuário pedir passo a passo.

## Organização
- Cada projeto vive em `projetos/<nome>/`, com seu próprio `README.md`
  (objetivo, como rodar, status).
- Não misture arquivos de projetos diferentes.
- Documentação geral fica em `docs/`. Rascunhos de skills ficam em `skills/`.
- Use nomes de pasta e arquivo em minúsculas, sem espaços (`meu-projeto`,
  não `Meu Projeto`).

## Regras de trabalho
- Antes de apagar ou sobrescrever arquivos existentes, confirme com o usuário.
- Não adicione chaves, senhas ou tokens ao repositório.
- Commits em português, mensagem curta e descritiva.
- Compatibilidade com Windows: evite caminhos longos e nomes com caracteres
  inválidos (`: * ? " < > |`).

## Custos
- O usuário quer usar os créditos de sessão na nuvem, não o plano do PC.
  Prefira criar e editar arquivos aqui e entregar comandos para ele rodar,
  em vez de depender de sessões locais.
