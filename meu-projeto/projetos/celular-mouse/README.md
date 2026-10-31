# Celular Mouse

## Objetivo
Usar o celular como mouse do PC Windows, sem instalar nada (o celular usa só o
navegador). Três modos (botões no topo da tela do celular):

- **Base (principal):** você **desliza o celular numa mesa ou mousepad**, como um
  mouse de verdade. A câmera de trás funciona como o sensor óptico de um mouse.
  A tela só tem os botões, nos lugares dos seus dedos.
- **Ar:** você move o celular no ar e o cursor acompanha (giroscópio). Ficou em
  segundo plano: ele só mede giro, não posição, e por isso "anda" um pouco.
- **Toque:** a tela do celular vira um touchpad.

## Status
`pausado` (2026-10-31) — decisão do usuário após os testes reais. O modo Toque
funciona; o modo Base (câmera) rastreia, mas ficou abaixo do esperado, e por
navegador há um teto físico (30–60 leituras/s, ~10–30 cm/s). Para retomar, o
caminho mais promissor é um app Android nativo (câmera de alta velocidade).

## Como rodar
1. No PC, **duplo clique em `iniciar.bat`** (pasta `projetos\celular-mouse`).
   Na primeira vez ele cria o `cert.pfx` e o Windows pergunta sobre o Firewall:
   marque **Redes particulares** e **Permitir acesso**.
2. Abre uma janela com um **QR code** (aba "Com sensor"). No celular, no mesmo
   Wi-Fi, escaneie com a câmera e toque no link.
3. O navegador avisa **"conexão não é particular"**: toque em **Avançado** e
   **Continuar** (o certificado é do seu PC; câmera e giroscópio exigem https).
4. **Imprima a folha de textura** (link na janela do QR, ou `/padrao` no
   navegador do PC) e cole na mesa: uma mesa lisa não tem nada para a câmera
   "enxergar".

## Modo Base: como usar
1. Toque em **Iniciar** e permita a **câmera**. A lanterna acende (ela
   funciona como o LED de um mouse óptico).
2. Na primeira vez abre a **calibração**: apoie o celular na folha, **reto,
   como um mouse**, e (1) toque em Começar e deslize **10 cm para a frente**,
   pare; (2) volte, toque em Começar e deslize **10 cm para a direita**, pare.
   Ela descobre a direção da câmera (são só 8 possibilidades: eixos trocados
   ou espelhados) e a escala, e deixa em 800 DPI. Deslizes tortos não entortam
   o resultado.
3. **Confira na "mira"** (círculo no canto da tela): deslize para a direita e
   a bolinha deve ir para a direita; para a frente, para cima. Se estiver ao
   contrário, é só marcar em ⚙: **Inverter ← →**, **Inverter ↑ ↓** ou
   **Trocar eixos**, sem precisar recalibrar.
4. A janelinha embaixo mostra a câmera, os quadros por segundo, o **% de
   rastreio**, a textura (`boa` / `fraca` / `só numa direção` / `sem textura`)
   e `rastreando` / `perdido`. "Só numa direção" é veio de madeira ou
   listras: o movimento ao longo delas não é medido; use a folha impressa.
5. **PAUSA** (segurar) congela o cursor para reposicionar o celular.
   ⚙ › **Detectar levantar** (experimental, desligado) congela sozinho quando
   o brilho muda de repente; pode disparar à toa ao passar por manchas
   claras e escuras da folha.
6. ⚙: **Sensibilidade (DPI)**, **Lanterna**, **Calibrar movimento**,
   **Trocar câmera** e **Mudar botões de lugar**.

| Botão | O que faz |
|---|---|
| ESQUERDO / DIREITO / MEIO | Cliques (dá para segurar e arrastar) |
| ▲ / ▼ | Roda do mouse (segurando, repete) |
| PAUSA | Segurar = congela o cursor |

### Limites do modo Base (leia)
- **Velocidade máxima.** A câmera do navegador entrega 30–60 quadros por
  segundo e enxerga só alguns milímetros da superfície. O rastreador aguenta
  cerca de 12% do campo de visão por quadro (até uns 25% em movimento contínuo,
  porque ele prevê o quadro seguinte), o que dá algo como **10–30 cm/s**.
  Serve para apontar, arrastar e mirar devagar; **flicks rápidos de jogo
  vão "perder" o movimento** (o cursor para em vez de pular para um lugar errado).
- **Foco.** A câmera fica a poucos milímetros da superfície, mais perto do que
  a maioria das câmeras foca. Imagem desfocada ainda funciona (a folha de
  textura tem manchas grandes de propósito), mas melhora muito se o celular
  tiver capinha grossa (afasta a lente) ou se **Trocar câmera** achar uma lente
  que foca perto (macro / ultra-angular).
- **Superfície.** Precisa de textura. Vidro, mesa branca lisa ou mousepad
  liso: `sem textura`. Use a folha impressa.
- **Taxa.** O cursor atualiza no ritmo da câmera (30–60 Hz), não 1000 Hz como
  um mouse. É perceptível em jogos rápidos.
- Se `rastreando` não aparece ao deslizar devagar, abra a janelinha da câmera:
  imagem preta = pouca luz (ligue a Lanterna); imagem lisa = falta textura.

## Modo Ar (girar o celular)
Gire para os lados = cursor na horizontal; incline = vertical (você mira com a
traseira, como numa janela). Se uma direção ficar ao contrário: ⚙ › Inverter.
⚙ › **Calibrar giroscópio** com o celular parado. O giroscópio tem desvio e só
mede giro, então não é preciso como o modo Base.

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
- **Pede cartão inteligente / PIN ao abrir (versão antiga):** vinha do
  certificado guardado na loja do Windows. Agora o certificado é só o arquivo
  `cert.pfx` desta pasta. Se ainda aparecer algo, rode `iniciar.bat -SemHttps`
  (liga só o modo toque, sem certificado) e me diga em que momento aparece.
  A versão antiga pode ter deixado o certificado "Celular Mouse" no Windows:
  é inofensivo, e dá para remover em `certmgr.msc` › Pessoal › Certificados.
- **Sensor sem HTTPS (só Chrome no Android):** abra `chrome://flags`, procure
  **"Insecure origins treated as secure"**, ative, escreva
  `http://IP-DO-PC:8765` (o endereço do QR "só toque"), toque em Relançar e
  abra o link http. Não existe equivalente no iPhone.
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
- **Limite dos sensores:** giroscópio e câmera chegam ao navegador a 30–60
  vezes por segundo (16–33 ms entre leituras). Somado ao Wi-Fi (2–10 ms), são
  algumas dezenas de ms: bom para desktop e mira lenta, limitado para jogo
  competitivo. Wi-Fi 5 GHz e perto do roteador ajuda.

## Estrutura
| Arquivo | Para que serve |
|---|---|
| `iniciar.bat` | Duplo clique para ligar |
| `servidor.ps1` | Cria o `cert.pfx` (1ª vez), compila e inicia o servidor |
| `certificado.cs` | Gera o certificado HTTPS (exige .NET Framework 4.7.2+, Windows 10/11 atual) |
| `servidor.cs` | Servidor: HTTP + HTTPS + WebSocket + `SendInput` |
| `web/index.html` | Tela do celular (Base, Ar, Toque, botões, ajustes) |
| `web/fluxo.js` | Rastreador de movimento pela câmera (fluxo óptico, Lucas-Kanade em pirâmide) |
| `web/padrao.html` | Folha de textura para imprimir |
| `web/qr.html`, `web/qrcode.js` | Página do QR no PC (`qrcode-generator`, MIT) |
| `liberar-firewall.bat` | Opcional: libera as portas 8765-8774 no Firewall |

## Segurança
- Só quem tem o link com a senha (`?t=...`, gerada no PC, guardada em
  `.token`, fora do Git) controla o mouse. O QR só abre no próprio PC.
- O HTTPS usa um certificado só seu (`cert.pfx` nesta pasta, fora do Git; CN=Celular Mouse).
  Protege a conversa na rede, mas o navegador do celular
  não "confia" nele, por isso o aviso. Use em redes de confiança.
- Limite do Windows: não controla janelas "como administrador" nem a tela de
  bloqueio/UAC, a menos que o `iniciar.bat` rode como administrador.

## Decisões e anotações
- 2026-10-31 (ajuste após o 1º teste real do modo Base: direção invertida e
  linhas tortas/falhadas): a calibração agora escolhe entre as 8 orientações
  possíveis (antes ajustava uma matriz livre, que absorvia qualquer curva dos
  deslizes); o fim de cada passo só conta com rastreio válido (antes perder o
  rastreio encerrava o passo cedo); o rastreador prevê o movimento a partir do
  quadro anterior (aceleração 0→30 px/quadro: de 17 falhas em 30 para 0) e
  rejeita medidas ruins/saltos (antes aceitava alguns resultados errados em
  alta velocidade); correção da proporção do vídeo; "levantar" passou a ser
  opcional (desligado) por risco de falso disparo.
- 2026-10-31: o usuário não quer mover o celular no ar, e sim deslizá-lo numa
  base como um mouse. Giroscópio/acelerômetro não dão posição (a integração
  dupla acumula erro), então o modo Base usa a câmera traseira como sensor
  óptico: fluxo óptico global por quadro (`fluxo.js`), calibração de 2 deslizes
  que resolve rotação/espelhamento/escala numa matriz 2x2, detecção de
  "levantou" por salto de brilho. Medido em teste sintético: erro < 0.01 px,
  ~0,4 ms por quadro, alcance ~15 px por quadro (em 128 px de largura).
- 2026-10-31: servidor em C# compilado pelo PowerShell (zero instalação).
  Código em C# 5 por causa do PowerShell 5.1.
- 2026-10-31: modo sensor com `devicemotion` (giroscópio + gravidade).
  A velocidade de giro é projetada na gravidade, então não depende da
  orientação da tela. Exige HTTPS (regra dos navegadores); por isso o
  certificado local e a porta 8766.
- Movimento por `SendInput` relativo (também chega como entrada bruta nos jogos).
- 2026-10-31: o certificado saiu da loja do Windows (`New-SelfSignedCertificate`)
  porque o usuário recebeu pedido de cartão inteligente; agora é gerado em
  código (`CertificateRequest`) e guardado em `cert.pfx`.
- Testado na nuvem (Mono + Chromium com sensores simulados): direção do
  cursor em pé/de lado/deitado, calibração, pausa, botões, edição de layout,
  HTTPS/wss. **Não testado:** `SendInput`/certificado no Windows e o
  giroscópio de um celular real.

## Próximos passos
- [ ] **Testar o modo Base com a câmera do celular real** (foco, textura, velocidade máxima).
- [ ] Base: ler a câmera em resolução/FPS maiores quando o celular permitir; exposição manual curta (menos borrão).
- [ ] Base: ajuste fino da detecção de "levantou" com a câmera real.
- [ ] Teclado (WASD / digitar) no celular.
- [ ] Mais botões configuráveis (teclas extras para jogos).
