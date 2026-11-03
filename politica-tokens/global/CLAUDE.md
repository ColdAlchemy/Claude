# Política global de eficiência (vale para qualquer projeto)

Objetivo: gastar menos tokens sem reduzir a qualidade. Nada abaixo autoriza pular verificação
nem encurtar o raciocínio necessário. Economize em ruído, não em rigor.

## Explorar sem desperdício
- Busque com Grep/Glob específicos antes de ler arquivos. Em arquivo grande, leia só o trecho
  necessário (offset/limit). Não releia arquivo já lido nesta conversa, salvo se ele mudou.
- Não varra o repositório inteiro por padrão. Se o pedido for vago demais para localizar o
  alvo, faça uma pergunta curta em vez de explorar às cegas.
- Antes de uma tarefa ampla ou com mais de um caminho possível, apresente o plano em poucas
  linhas e espere confirmação. Refazer trabalho custa mais que planejar.

## Executar e verificar
- Todo trabalho termina com a verificação do próprio projeto (testes, lint, tipos, build) sobre
  o que foi alterado. Só declare "pronto" depois de ver o resultado. Se falhar, mostre o erro
  real, não um resumo otimista.
- Comandos com saída potencialmente longa: filtre com `tail`, `grep` ou flags de modo quieto,
  mas nunca esconda falhas e preserve o código de saída.
- Uma execução focada (arquivo ou teste afetado) antes da suíte completa. A suíte completa
  roda uma vez no fim, não a cada edição.

## Responder
- Resposta final curta: o que mudou, como foi verificado, o que ficou pendente ou incerto.
  Sem recapitular o que o usuário acabou de ler, sem elogios, sem repetir o diff.
- Não crie arquivos de documentação, relatórios ou testes extras que não foram pedidos.
- Quando algo for incerto, diga o que não foi verificado em vez de afirmar.

## Delegar com critério
- Subagentes custam tokens extras. Use só para saída volumosa que poluiria a conversa ou para
  revisão independente. Para tarefa pequena, faça direto. Prefira o modelo menor em subagentes
  de busca simples.
- Não inicie loops, agentes paralelos ou tarefas agendadas sem o usuário pedir.

## Higiene da conversa
- Depois de duas correções sobre o mesmo ponto sem sucesso, sugira `/clear` e um prompt
  reescrito, em vez de insistir na mesma conversa.
- Ao terminar uma tarefa e o usuário mudar de assunto, lembre-o de usar `/clear`.

# Compact instructions
Ao compactar, preserve: decisões tomadas e o motivo, arquivos alterados, comandos de
verificação e seus resultados, erros ainda abertos, pendências. Descarte saídas longas já
resolvidas e tentativas descartadas.
