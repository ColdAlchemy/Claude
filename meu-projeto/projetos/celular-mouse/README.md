# Celular Mouse

## Objetivo
Usar o celular como mouse/touchpad do PC Windows, com latência mínima e sem
instalar nada: nem no PC, nem no celular (o celular usa só o navegador).

## Status
`em andamento` — código pronto e testado na nuvem (protocolo, gestos,
segurança). Falta o primeiro teste real no PC Windows.

## Como rodar
1. No PC, dê **duplo clique em `iniciar.bat`** (pasta `projetos\celular-mouse`).
2. Abre uma janela do navegador com um **QR code**. Na primeira vez o Windows
   pergunta sobre o Firewall: marque **Redes particulares** e clique em
   **Permitir acesso**.
3. No celular (no **mesmo Wi-Fi**), abra a câmera, aponte para o QR code e
   toque no link. Pronto.

Dica: no celular, "Adicionar à tela inicial" no menu do navegador cria um
ícone. Da próxima vez, é só rodar `iniciar.bat` e tocar no ícone (o endereço
só muda se o IP do PC mudar; aí escaneie o QR de novo).

## Gestos

| Gesto | O que faz |
|---|---|
| Arrastar 1 dedo | Move o cursor |
| Tocar | Clique esquerdo |
| Tocar com 2 dedos | Clique direito |
| Tocar com 3 dedos | Clique do meio |
| Arrastar 2 dedos (ou a faixa ROLAR) | Rolar (vertical e horizontal) |
| Tocar, tocar de novo e arrastar | Segurar e arrastar (selecionar, mover janela) |
| Botões ESQUERDO / MEIO / DIREITO | Botões do mouse (dá para segurar e mexer com a outra mão) |

Engrenagem (⚙): velocidade, aceleração, rolagem, tocar para clicar, vibração.
O número ao lado de "Conectado" é o tempo de ida e volta até o PC, em ms.

## Se não conectar
- Celular e PC precisam estar na mesma rede. Wi-Fi de visitantes ou
  "isolamento de clientes" do roteador bloqueia. Alternativa: ligar o
  roteador do celular (hotspot) e conectar o PC nele.
- Rede do Windows como "Pública" bloqueia: mude para "Particular" ou rode
  `liberar-firewall.bat` (pede permissão de administrador).
- O QR mostra mais de um endereço? Clique no botão da rede certa (Wi-Fi).
- Trocar a senha do link (invalida o QR antigo): apague o arquivo `.token`
  e rode de novo.

## Como é rápido
- Conexão WebSocket direta celular -> PC, mensagens binárias de 5 bytes.
- `TCP_NODELAY` ligado (sem espera de Nagle) no servidor.
- Cada evento de toque vira uma mensagem na hora, sem fila: se a rede
  engarrafar, os movimentos são somados em vez de empilhados, então o cursor
  nunca "se arrasta" atrasado.
- O PC injeta o movimento direto com `SendInput`, sem intermediários.
- Medido na nuvem (localhost): ~0,1 ms de processamento no servidor. O resto
  é o Wi-Fi (tipicamente 2–10 ms; 5 GHz e perto do roteador é melhor).

## Estrutura
| Arquivo | Para que serve |
|---|---|
| `iniciar.bat` | Duplo clique para ligar |
| `servidor.ps1` | Compila e inicia o servidor (PowerShell já vem no Windows) |
| `servidor.cs` | O servidor: HTTP + WebSocket + `SendInput` |
| `web/index.html` | A tela do celular (touchpad, gestos, ajustes) |
| `web/qr.html`, `web/qrcode.js` | Página do QR no PC (biblioteca `qrcode-generator`, MIT) |
| `liberar-firewall.bat` | Opcional: libera a porta no Firewall |

## Segurança
- Só quem tem o link com a senha (`?t=...`, gerada no PC, guardada em
  `.token` e fora do Git) consegue controlar o mouse. O QR só abre no próprio PC.
- Não há criptografia (HTTP simples na rede local): use em redes de confiança.
- Limite do Windows: não controla janelas abertas "como administrador" nem a
  tela de bloqueio/UAC, a menos que o `iniciar.bat` também rode como administrador.

## Decisões e anotações
- 2026-10-31: servidor em C# compilado pelo PowerShell (zero instalação) em
  vez de Python/Node, porque o usuário prefere evitar terminal e instalações.
  Código em C# 5 por causa do PowerShell 5.1.
- Cliente é página web, não app: nada para instalar no celular.
- Movimento relativo por `SendInput`; a aceleração do próprio Windows também
  vale. Se ficar rápido/lento demais, ajuste em ⚙.
- Testado na nuvem com Mono (compilação C# 5, protocolo, token, soltar botão
  ao desconectar) e Chromium com toques simulados. **Não testado** no Windows
  real: `SendInput`, descoberta de IP e o Firewall.

## Próximos passos
- [ ] Testar no PC real e ajustar velocidade/aceleração padrão.
- [ ] Teclado (digitar texto pelo celular).
- [ ] Modo giroscópio (apontar o celular), exige HTTPS no celular.
- [ ] Manter a tela do celular acordada (Wake Lock/NoSleep).
