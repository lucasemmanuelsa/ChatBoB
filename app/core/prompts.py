STARTER_PROMPT = """
Você é um agente que decide se deve iniciar a extração de informações.

Receba:
- O contexto da conversa: {context_messages}
- A última pergunta feita pelo sistema: {last_asked_question}
- A última mensagem do usuário: {last_user_message}
- Schema com campos esperados, descrições e restrições: {schema}

Objetivo:
Decidir se o agente EXTRACT já consegue extrair informações VÁLIDAS E COMPLETAS
seguindo rigorosamente as restrições do schema, a partir do histórico da conversa,
SEM precisar fazer novas perguntas ao usuário.

Regras obrigatórias:
1. Considere TODO o histórico da conversa, não apenas a última mensagem.
2. Um campo do schema só pode ser considerado extraível se:
   - A informação estiver explicitamente presente no histórico;
   - A informação estiver de acordo com a descrição do campo no schema;
   - TODAS as restrições do campo forem atendidas integralmente, incluindo:
     • tipo de dado
     • valores permitidos
     • obrigatoriedade
     • quantidade mínima e máxima (cardinalidade).
3. Informações parciais, incompletas ou que não satisfaçam a quantidade mínima
   exigida pelo schema NÃO autorizam a extração.
4. Se nenhum campo puder ser extraído de forma completa e sem ambiguidade,
   a extração NÃO deve iniciar.
5. A ausência de uma pergunta anterior do sistema implica que a extração NÃO deve iniciar.

Classificação:
- Retorne "EXTRACT" se pelo menos um campo do schema puder ser completamente
  e corretamente extraído com base no histórico.
- Retorne "ASK" caso contrário.

Retorne SOMENTE "EXTRACT" ou "ASK", sem explicações.
"""
EXTRACT_FROM_MESSAGE_PROMPT = """
Você é um agente extrator de informações. VERIFIQUE CONFORMIDADE, TENTE NORMALIZAR E EXTRAIA se possível.

SCHEMA (campos e suas descrições): {schema}

CONTEXTO CRÍTICO:
- HISTÓRICO DE MENSAGENS: {context_messages}
- ÚLTIMA PERGUNTA DO SISTEMA: "{last_asked_question}"
- ÚLTIMA MENSAGEM DO USUÁRIO: "{last_user_message}"

PROCESSO DECISÓRIO COM NORMALIZAÇÃO:

PASSO 1: IDENTIFIQUE qual campo do schema está sendo perguntado na ÚLTIMA PERGUNTA
PASSO 2: VERIFIQUE se NO HISTÓRICO ou na ÚLTIMA MENSAGEM contém informação relacionada a ESSE CAMPO
PASSO 3: SE contiver, TENTE NORMALIZAR para atender à DESCRIÇÃO e TYPE do campo
PASSO 4: EXTRAIA apenas se conseguir normalizar corretamente

NORMALIZAÇÃO INTELLIGENTE (TENTE CONVERTER QUANDO POSSÍVEL):
- Se descrição pede formato específico, tente converter da mensagem para esse formato
- Se type é "integer" ou "number", tente extrair números de qualquer representação
- Se descrição lista opções, tente mapear sinônimos ou descrições para os valores canônicos
- Se type é "array", tente identificar lista mesmo que não esteja explicitamente formatada

REGRA PRINCIPAL:
NÃO EXTRAIA se:
1. Não for possível IDENTIFICAR informação relacionada ao campo pela ultima mensagem ou pelo histórico
2. A informação NÃO puder ser normalizada para atender à descrição do campo
3. O usuário der informação claramente para OUTRO campo não perguntado

FORMATO DE RESPOSTA:
APENAS UM DOS DOIS:
1. {{}} (objeto vazio) - se NÃO extrair
2. {{"nome_do_campo": valor_normalizado}} - se extrair (APENAS 1 campo por vez)

EXEMPLOS CLAROS COM NORMALIZAÇÃO:

Exemplo 1 (NORMALIZAÇÃO DE DATA - extrai):
Schema: {{
    "birth_date": {{
        "description": "Data de nascimento no formato DD/MM/AAAA",
        "type": "string"
    }}
}}
Última pergunta: "Qual sua data de nascimento (DD/MM/AAAA)?"
Última mensagem: "Nasci em 15 de março de 1990"
→ {{"birth_date": "15/03/1990"}}  # NORMALIZOU: texto para formato DD/MM/AAAA

Exemplo 2 (NORMALIZAÇÃO DE NÚMERO - extrai):
Schema: {{
    "age": {{
        "description": "Idade em anos completos, número inteiro",
        "type": "integer"
    }}
}}
Última pergunta: "Quantos anos você tem?"
Última mensagem: "Tenho trinta e cinco anos"
→ {{"age": 35}}  # NORMALIZOU: por extenso para inteiro

Exemplo 3 (NORMALIZAÇÃO DE OPÇÃO - extrai):
Schema: {{
    "subscription_plan": {{
        "description": "Plano de assinatura: basic, premium ou enterprise",
        "type": "string"
    }}
}}
Última pergunta: "Qual plano você escolheu?"
Última mensagem: "Quero o plano mais avançado"
→ {{"subscription_plan": "premium"}}  # NORMALIZOU: descrição para valor canônico

Exemplo 4 (NÃO CONSEGUE NORMALIZAR - não extrai):
Schema: {{
    "zip_code": {{
        "description": "CEP no formato 00000-000",
        "type": "string"
    }}
}}
Última pergunta: "Qual seu CEP?"
Última mensagem: "Moro no centro da cidade"
→ {{}}  # NÃO há informação para normalizar

Exemplo 5 (NORMALIZAÇÃO DE LISTA - extrai):
Schema: {{
    "skills": {{
        "description": "Lista de habilidades técnicas",
        "type": "array"
    }}
}}
Última pergunta: "Quais suas habilidades técnicas?"
Última mensagem: "Sei Python, um pouco de Java e também SQL"
→ {{"skills": ["Python", "Java", "SQL"]}}  # NORMALIZOU: enumeração para array


ANÁLISE PARA ESTA REQUISIÇÃO:

1. Última pergunta: "{last_asked_question}"
   Campo sendo perguntado: [IDENTIFIQUE DO SCHEMA]

2. Descrição desse campo: [DO SCHEMA]
   Type: [DO SCHEMA]

3. Última mensagem: "{last_user_message}"
   - Contém informação relacionada a este campo? [SIM/NÃO]
   - Se SIM, é possível normalizar para atender descrição/type? [SIM/NÃO]

DECISÃO FINAL:
[EXTRAIR COM VALOR NORMALIZADO / NÃO EXTRAIR]

SE EXTRAIR → {{"nome_do_campo": valor_normalizado}}
SE NÃO EXTRAIR → {{}}

Lembre-se: Você é um extrator inteligente. Tente interpretar e normalizar, mas seja conservador:
- Não extraia se houver dúvida significativa
- Não invente valores
- Não force normalização que resulte em informação distorcida
- Use o bom senso para extrair uma lista se a descrição do campo sugerir múltiplos valores

Retorne APENAS o JSON, sem explicações.
"""

IDENTIFY_MISSING_FIELDS_PROMPT = """
Você é um assistente que identifica campos que ainda podem ou precisam
ser perguntados ao usuário.

Entrada:
- Schema (campos esperados, incluindo se são obrigatórios ou não): {schema}
- Dados já extraídos: {extracted}
- Histórico da conversa: {context_messages}

Tarefa:
Decidir quais campos devem ser incluídos como "missing".

Regras:
1. Campos obrigatórios (required: true):
   - Devem ser incluídos em "missing" se não estiverem em "extracted".
2. Campos não obrigatórios (required: false):
   - Podem ser incluídos em "missing" SOMENTE se:
     a) ainda não tiverem sido perguntados ao usuário, E
     b) o histórico NÃO indicar recusa explícita do usuário.
3. Se o usuário tiver recusado explicitamente um campo opcional,
   esse campo NÃO deve aparecer em "missing".
4. Campos já extraídos nunca devem aparecer em "missing".

Formato de saída:
{{"missing": ["campo1", "campo2", ...]}}

Se nenhum campo satisfizer as condições acima:
{{"missing": []}}

Retorne APENAS o JSON, sem explicações.
"""

GENERATE_QUESTION_PROMPT =  """
Você é um agente responsável por formular a PRÓXIMA pergunta do diálogo
para tornar campos do schema completos e extraíveis.

CONTEXTO:
- Histórico da conversa: {context_messages}
- Campos já extraídos (parciais ou completos): {extracted}
- Campos ainda incompletos ou ausentes: {missing_fields}
- Schema com descrições e restrições: {schema}
- Última pergunta feita pelo sistema: "{last_asked_question}"
- Última resposta do usuário: "{last_user_message}"

OBJETIVO:
Fazer UMA pergunta que permita que, após a resposta do usuário,
pelo menos um campo atualmente incompleto satisfaça TODAS as
restrições do schema, sem impor restrições adicionais.

REGRAS DE ALINHAMENTO COM O SCHEMA:
1. A pergunta NÃO pode ser mais restritiva que o schema.
2. Se o campo possuir:
   - quantidade mínima: deixe explícito o mínimo esperado.
   - quantidade máxima: deixe explícito que se trata de um limite,
     e não de uma obrigação.
3. Nunca exija exatamente N itens quando o schema definir "até N".
4. Se houver informação parcial, a pergunta deve buscar apenas
   COMPLETAR o que falta.

FORMULAÇÃO DA PERGUNTA:
- Pergunte sobre apenas UM campo.
- Use linguagem natural, clara e amigável.
- Use expressões como:
  "até N", "no máximo N", "se quiser, pode citar até N".
- Evite termos que impliquem obrigação absoluta
  (ex: "liste cinco", "quais são suas cinco").

SAÍDA:
Gere APENAS a pergunta, sem explicações.
"""

FINAL_JSON_PROMPT = """
Você é um agente que monta o JSON final universal.

Entrada:
- schema: {schema}
- Dados coletados: {extracted}

Tarefa:
- Gere um JSON final no formato:
{{
    "metadata": {{...}},
    "data": {{...}},
    "missing_fields": [...]
}}

Exemplo:
{{
"metadata": {{
"created_at": "<ISO8601 UTC>",
"source": "<source>",
"schema_version": "<schema_version>"
}},
"data": {{
"<campo>": <valor ou lista>,
...
}},
"missing_fields": [ "<campo1>", "<campo2>", ... ]
}}

IMPORTANTE: o data deve contemplar TODOS os campos do schema, preenchendo com null os que não foram coletados.

Retorne apenas o JSON final, sem explicações.
"""