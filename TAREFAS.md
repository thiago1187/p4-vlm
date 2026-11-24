# P4 · Divisão de tarefas

**Prazo:** apresentação presencial na **segunda, 30/11**. A nota considera o repositório como estiver no prazo.
**Nota:** 30% originalidade · 30% app com VLM · 40% apresentação (cada integrante precisa estar presente e falar).

## Já pronto no repositório
- `vlm_client.py`: `perguntar_vlm`, `extrair_json`, `img_para_data_url` do notebook da Aula 09, com a chave lida do `.env`
- `app.py`: Streamlit com upload/câmera, botão Analisar, JSON na tela, erros e histórico
- `prompts.py`: prompt de sistema anti-alucinação + esquema de exemplo (trocar pela nossa ideia)
- `avaliar.py`: roda o VLM nas imagens de `exemplos/` e calcula a acurácia por campo
- `requirements.txt`, `.env.example`, `.gitignore` (o `.env` nunca vai para o GitHub)

## Todos juntos (hoje/amanhã)
- [ ] Escolher a ideia e escrever a frase: *"Para <usuário>, que precisa <tarefa>, o app recebe <imagem> e devolve <saída>"*
- [ ] Cada um cria sua chave em console.groq.com (plano gratuito tem limite por minuto, então é melhor ter 3 chaves)
- [ ] Definir o esquema JSON de saída (os campos)

## Pessoa 1 · Modelo e prompt
- [ ] Trocar `PROMPT` e `CAMPOS_OBRIGATORIOS` em `prompts.py` pelo esquema da ideia
- [ ] Testar o prompt com 3-4 imagens antes de ir para o app; ajustar até o JSON sair estável
- [ ] Testar uma pergunta com premissa falsa (Aula 09 · 3.7) e ver se o prompt de sistema segura
- [ ] **Apresenta:** problema, usuário, por que VLM e não YOLO/CLIP, o prompt e o esquema JSON

## Pessoa 2 · Interface
- [ ] Dar nome ao app e mostrar o resultado de forma legível (cards, tabela, alertas), mantendo o JSON num expander
- [ ] Conferir as mensagens de erro: sem chave, imagem PNG, JSON inválido, limite de taxa
- [ ] Tirar os prints (ou gravar um vídeo curto) do app funcionando
- [ ] **Apresenta:** a demo ao vivo e por que escolhemos Streamlit

## Pessoa 3 · Testes e documentação
- [ ] Juntar pelo menos 5 imagens reais em `exemplos/` (fotos nossas, não da internet de preferência)
- [ ] `python avaliar.py rodar`, preencher à mão `esperado` e `acertou` no `avaliacao.csv`, depois `python avaliar.py acuracia`
- [ ] Separar pelo menos 2 erros reais do modelo e o que fizemos para reduzir
- [ ] Puxar a escrita do README (tem que ser autoral, com a declaração de uso de IA)
- [ ] **Apresenta:** tabela de acurácia, os erros e as limitações (alucinação, contagem, custo em tokens)

## Slides (10-15 min) · cada um faz os slides da sua parte
1. Problema e usuário (P1)
2. Por que VLM (P1)
3. Prompt + esquema JSON (P1)
4. Demo ao vivo (P2)
5. Acurácia por campo (P3)
6. Erros reais e o que fizemos (P3)
7. Limitações e próximos passos (P3)

## Cronograma
| Dia | O quê |
|---|---|
| Ter 24 | Ideia escolhida, chaves criadas, repositório no GitHub |
| Qua 25 | P1 prompt funcionando · P2 interface · P3 coleta e anota imagens |
| Qui 26 | Integrar prompt no app · P3 roda a avaliação |
| Sex 27 | Ajustar o prompt com base nos erros · README |
| Sáb 28 | Slides e prints |
| Dom 29 | Ensaio da apresentação · último push |
| Seg 30 | Apresentação |

## Como rodar
```bash
pip install -r requirements.txt
cp .env.example .env   # cole sua GROQ_API_KEY
streamlit run app.py
```
