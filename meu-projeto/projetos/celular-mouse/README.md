# Celular Mouse

## Objetivo
Usar o celular como mouse do PC Windows, com latência mínima e sem instalar
nada (o celular usa só o navegador). Dois modos:

- **Sensor (para jogar):** você *move o celular no ar* e o cursor acompanha,
  como um mouse aéreo / mira por giroscópio. A tela só tem botões, nos
  lugares onde seus dedos ficam.
- **Toque:** a tela do celular vira um touchpad.

## Status
`em andamento` — modo toque testado em uso real no PC. Modo sensor testado na
nuvem com movimentos simulados; **falta o primeiro teste real** (giroscópio do
seu celular + HTTPS no Windows).

## Como rodar
1. No PC, dê **duplo clique em `iniciar.bat`** (pasta `projetos\celular-mouse`).
   Na primeira vez ele cria um certificado local (alguns segundos) e o Windows
   pergunta sobre o Firewall: marque **Redes particulares** e **Permitir acesso**.
2. Abre uma janela com um **QR code**. Deixe a aba **"Com sensor (jogos)"**.
3. No celular (mesmo Wi-Fi), aponte a câmera para o QR code e toque no link.
4. O navegador avisa **"conexão não é particular"**. É normal (o certificado é
   do seu próprio PC; o giroscópio só funciona em páginas https). Toque em
   **Avançado** e depois em **Continuar**. Só na primeira vez.
5. Toque em **Iniciar**, deixe o celular parado por 1 segundo (calibração) e
   pronto: gire o celular.

Dica: no menu do navegador, "Adicionar à tela inicial" cria um ícone.

## Modo sensor: como funciona
- **Girar para os lados** move o cursor na horizontal; **inclinar para cima/baixo**
  move na vertical. Você mira com a **traseira** do celular, como se ele
  fosse uma janela: apontou a traseira para a esquerda, o mouse vai para a
  esquerda. Funciona em pé, de lado (paisagem) ou deitado.
- Se alguma direção ficar ao contrário: ⚙ → **Inverter horizontal/vertical**.
- **PAUSA** (segurar) congela o cursor, como levantar o mouse da mesa: use
  para voltar o celular à posição confortável sem mover a mira.
- O giroscópio tem um pequeno "desvio" com o tempo. Ele se corrige sozinho
  quando o celular fica parado; se a mira "andar", use ⚙ → **Calibrar agora**.
- A tela do celular não apaga enquanto você usa (Wake Lock).

### Botões: você escolhe onde ficam
⚙ → **Mudar botões de lugar**: arraste cada botão para onde seus dedos ficam
melhor e use a barra para mudar o tamanho (toque no botão para selecioná-lo).
O layout é guardado separado para celular em pé e deitado.

| Botão | O que faz |
|---|---|
| ESQUERDO / DIREITO / MEIO | Cliques (dá para segurar) |
| ▲ / ▼ | Roda do mouse (segurando, repete) — troca de arma, zoom |
| PAUSA | Segurar = congela o cursor |

Ajustes (⚙): sensibilidade horizontal e vertical, inversão, calibrar, botões.

## Modo toque
| Gesto | O que faz |
|---|---|
| Arrastar 1 dedo | Move o cursor |
| Tocar | Clique esquerdo |
| Tocar com 2 / 3 dedos | Clique direito / do meio |
| Arrastar 2 dedos (ou a faixa ROLAR) | Rolar |
| Tocar, tocar de novo e arrastar | Segurar e arrastar |

## Se não funcionar
- **Não conecta:** celular e PC na mesma rede. Wi-Fi de visitantes ou
  "isolamento de clientes" bloqueia; alternativa: ligar o hotspot do celular e
  conectar o PC nele. Rede do Windows como "Pública" bloqueia: mude para
  "Particular" ou rode `liberar-firewall.bat` (pede administrador).
- **Mostra "Falta o HTTPS":** abriu o link http. Use o QR da aba "Com sensor".
  Se o PC não conseguiu criar o certificado, o `iniciar.bat` mostra um aviso
  amarelo; me mande o texto.
- **Sensor bloqueado (iPhone):** Ajustes › Safari › Movimento e orientação.
- **Mais de um endereço no QR:** clique no botão da rede Wi-Fi certa.
- **Trocar a senha do link:** apague o arquivo `.token` e rode de novo.
- **Jogo ignora o mouse:** alguns jogos/anti-cheat bloqueiam entrada
  simulada, e janelas abertas "como administrador" também (rode o
  `iniciar.bat` como administrador nesse caso).
- **Cursor rápido/lento demais:** ⚙ sensibilidade. A aceleração de ponteiro
  do Windows também vale no desktop; em jogos, desligue
  "Aprimorar precisão do ponteiro" nas opções do mouse.

## Latência
- Conexão WebSocket direta (https/wss), mensagens binárias de 5 bytes,
  `TCP_NODELAY`, sem fila: se a rede engarrafar, os movimentos são somados em
  vez de empilhados.
- O PC injeta o movimento direto com `SendInput`.
- Medido na nuvem (localhost, com TLS): menos de 1 ms no servidor.
- **Limite do sensor:** o navegador entrega o giroscópio a ~60 vezes por
  segundo (≈ 16 ms entre leituras). Somado ao Wi-Fi (2–10 ms), fica na casa de
  20–30 ms. Para jogo competitivo, Wi-Fi 5 GHz e perto do roteador ajuda muito.

## Estrutura
| Arquivo | Para que serve |
|---|---|
| `iniciar.bat` | Duplo clique para ligar |
| `servidor.ps1` | Cria o certificado local, compila e inicia o servidor |
| `servidor.cs` | Servidor: HTTP + HTTPS + WebSocket + `SendInput` |
| `web/index.html` | Tela do celular (sensor, toque, botões, ajustes) |
| `web/qr.html`, `web/qrcode.js` | Página do QR no PC (`qrcode-generator`, MIT) |
| `liberar-firewall.bat` | Opcional: libera as portas 8765-8774 no Firewall |

## Segurança
- Só quem tem o link com a senha (`?t=...`, gerada no PC, guardada em
  `.token`, fora do Git) controla o mouse. O QR só abre no próprio PC.
- O HTTPS usa certificado do próprio PC (CN=Celular Mouse, na loja do seu
  usuário do Windows). Protege a conversa na rede, mas o navegador do celular
  não "confia" nele, por isso o aviso. Use em redes de confiança.
- Limite do Windows: não controla janelas "como administrador" nem a tela de
  bloqueio/UAC, a menos que o `iniciar.bat` rode como administrador.

## Decisões e anotações
- 2026-10-31: servidor em C# compilado pelo PowerShell (zero instalação).
  Código em C# 5 por causa do PowerShell 5.1.
- 2026-10-31: modo sensor com `devicemotion` (giroscópio + gravidade).
  A velocidade de giro é projetada na gravidade, então não depende da
  orientação da tela. Exige HTTPS (regra dos navegadores); por isso o
  certificado local e a porta 8766.
- Movimento por `SendInput` relativo (também chega como entrada bruta nos jogos).
- Testado na nuvem (Mono + Chromium com sensores simulados): direção do
  cursor em pé/de lado/deitado, calibração, pausa, botões, edição de layout,
  HTTPS/wss. **Não testado:** `SendInput`/certificado no Windows e o
  giroscópio de um celular real.

## Próximos passos
- [ ] Testar no PC e no celular reais; ajustar sensibilidade padrão e sinais.
- [ ] Menos latência: API `Gyroscope` do Chrome (taxa maior que 60 Hz).
- [ ] Teclado (WASD / digitar) no celular.
- [ ] Mais botões configuráveis (teclas extras para jogos).
