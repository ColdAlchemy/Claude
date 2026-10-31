# Fluxo nuvem -> PC

Como trazer para o seu PC o que o Claude cria na nuvem, e abrir no Antigravity.

## Primeira vez (uma vez só)

1. Instale o Git for Windows, se ainda não tiver: https://git-scm.com/downloads/win
   Confirme no PowerShell:

   ```powershell
   git --version
   ```

2. Escolha onde ficará a pasta, por exemplo a Área de Trabalho:

   ```powershell
   cd "$env:USERPROFILE\OneDrive\Área de Trabalho"
   ```

   Se o caminho acima não existir, use `cd "$env:USERPROFILE\Desktop"`.

   Dica: prefira uma pasta fora do OneDrive, como `C:\dev`, para evitar
   problemas de sincronização com a pasta `.git`.

3. Baixe o repositório na branch de trabalho:

   ```powershell
   git clone -b claude/peaceful-meitner-j086iy https://github.com/ColdAlchemy/Claude.git
   ```

   Se for repositório privado, o Git abre uma janela para você entrar na
   conta do GitHub. Faça o login e autorize.

4. Entre na pasta do projeto:

   ```powershell
   cd Claude\meu-projeto
   ```

5. No Antigravity: **File -> Open Folder**, selecione a pasta `meu-projeto`
   e confirme.

## Dia a dia

Sempre que o Claude avisar "enviei alterações":

```powershell
cd caminho\para\Claude
git pull
```

O Antigravity atualiza os arquivos sozinho. Se uma janela perguntar sobre
recarregar, aceite.

Ou use o script de apoio, a partir da pasta `meu-projeto`:

```powershell
.\scripts\atualizar.ps1
```

## Enviar alterações suas para a nuvem

Se você editar algo no Antigravity e quiser que o Claude veja:

```powershell
git add -A
git commit -m "Descrição curta da mudança"
git push
```

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| `git` não é reconhecido | Instale o Git for Windows e reabra o PowerShell. |
| `Authentication failed` | Entre de novo na conta do GitHub quando a janela abrir. |
| `Your local changes would be overwritten` | Faça commit das suas mudanças antes do `git pull`. |
| `branch not found` | Confirme o nome: `claude/peaceful-meitner-j086iy`. |
