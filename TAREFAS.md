# P4 · Plano de trabalho: calorias do prato

**Apresentação:** segunda, 30/11/2026, presencial, 10 a 15 min. Vale o estado do repositório nessa data.
**Nota:** 30% originalidade · 30% app com VLM · 40% apresentação (todos presentes e falando).

## Quem faz o quê (sugestão: troquem à vontade)
| Parte | Responsável | Apresenta |
|---|---|---|
| Modelo e prompt | Thiago | Problema, usuário, por que VLM, prompt e JSON |
| Interface | Henrique | Demo ao vivo e por que Streamlit |
| Testes e documentação | Alana | Acurácia, erros reais e limitações |

## O que precisa estar entregue em 30/11
- [ ] Link do repositório GitHub no Classroom
- [ ] `README.md` escrito pelo grupo: problema, usuário, modelo/API, como rodar, por que Streamlit, declaração de uso de IA
- [ ] `app.py` + `requirements.txt` + `.env.example` (sem chave!)
- [ ] Prints ou vídeo curto do app
- [ ] Tabela de avaliação com 5+ fotos reais (`avaliacao.csv`)
- [ ] Slides
- [ ] Apresentação com demo ao vivo, prompt, JSON e pelo menos 2 erros reais do modelo

---

## Parte 0 · Preparação (todos, ter 24)
- [x] Repositório criado e base do app pronta (`vlm_client.py`, `app.py`, `avaliar.py`)
- [x] Conexão com o Groq testada (`qwen/qwen3.8-27b`)
- [ ] Cada um cria sua chave em console.groq.com e o próprio `.env` (copiando o `.env.example`)
- [ ] Henrique aceita o convite do repositório · Alana envia o usuário do GitHub
- [ ] Cada um roda o app no próprio computador (passo a passo no fim)

## Parte 1 · Proposta (todos, ter 24 a qua 25)
- [ ] Escrever a frase: *"Para <usuário>, que precisa <tarefa>, o app recebe <imagem> e devolve <saída>"*
- [ ] Definir o diferencial: texto complementar ("comi só metade") + o app dizer quando não sabe
- [ ] Escrever o argumento "por que VLM e não YOLO ou CLIP"

## Parte 2 · Modelo e prompt (Thiago, qua 25 a qui 26)
- [ ] Trocar o prompt genérico de `prompts.py` pelo de calorias (alimentos, porção, kcal, total, confiança, observação)
- [ ] Regras no prompt de sistema: não inventar ingredientes, marcar o que não identificou, deixar claro que é estimativa
- [ ] Usar o texto opcional do usuário no prompt
- [ ] Validação: campos obrigatórios + total igual à soma dos alimentos
- [ ] Testar com 3 ou 4 fotos até o JSON sair estável

## Parte 3 · Interface (Henrique, qua 25 a sex 27)
- [ ] Campo de texto "informação extra" ao lado da foto
- [ ] Tabela com alimento, porção e calorias + total em destaque
- [ ] Aviso "resultado aproximado" e lista do que não foi identificado
- [ ] JSON completo escondido em "ver detalhes"
- [ ] Mensagens de erro claras (sem chave, sem internet, JSON inválido, limite de uso)
- [ ] Prints ou vídeo curto do app funcionando

## Parte 4 · Testes (Alana, qua 25 a sex 27)
- [ ] Tirar 6 a 8 fotos reais de pratos em `exemplos/` (incluir 1 ou 2 comidas com tabela nutricional)
- [ ] `python avaliar.py rodar` → preencher à mão `esperado` e `acertou` no `avaliacao.csv`
- [ ] Critério: *alimentos* acertou se reconheceu os principais itens · *kcal_total* acertou se ficou até ±30%
- [ ] `python avaliar.py acuracia` → tabela de acurácia por campo
- [ ] Separar 2 erros reais e testar uma correção (ex.: garfo ao lado como referência, texto complementar)
- [ ] Extra opcional: rodar a mesma foto 3 vezes e ver se as calorias mudam

## Parte 5 · README e slides (todos, sex 27 a sáb 28)
- [ ] README escrito pelo grupo (Alana puxa; o Claude só ajuda a organizar e revisar)
- [ ] Slides, cada um faz os da sua parte:
  1. Problema e usuário · 2. Por que VLM · 3. Prompt e JSON (Thiago)
  4. Demo ao vivo (Henrique)
  5. Acurácia · 6. Erros reais e o que fizemos · 7. Limitações (Alana)

## Parte 6 · Ensaio e entrega (todos, dom 29 a seg 30)
- [ ] Ensaio cronometrado (10 a 15 min)
- [ ] Rodar o app do zero com `pip install -r requirements.txt` para garantir que funciona
- [ ] Último push e link no Classroom
- [ ] Plano B da demo: prints/vídeo, caso a internet ou a API falhe na hora

---

## Como rodar
```bash
pip install -r requirements.txt
cp .env.example .env   # cole sua GROQ_API_KEY no .env (nunca no .env.example)
streamlit run app.py
```
