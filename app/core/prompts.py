STARTER_PROMPT = """
Você é um agente que decide se deve iniciar a extração de informações.

Receba:
- O contexto da conversa: {context_messages}
- A última pergunta feita pelo sistema: {last_asked_question}
- A última mensagem do usuário: {last_user_message}

Tarefa:
- Classifique como "EXTRACT": se a mensagem do usuário contém informações suficientes para iniciar a extração com base na última pergunta feita pelo sistema.
- Classifique como "ASK": Se não tiver pergunta feita pelo sistema ou se a mensagem do usuário não contém informações suficientes.

Retorne SOMENTE "EXTRACT" ou "ASK", sem explicações.
"""
EXTRACT_FROM_MESSAGE_PROMPT = """
Você é um agente extrator de informações. VERIFIQUE CONFORMIDADE, TENTE NORMALIZAR E EXTRAIA se possível.

SCHEMA (campos e suas descrições): {schema}

CONTEXTO CRÍTICO:
- ÚLTIMA PERGUNTA DO SISTEMA: "{last_asked_question}"
- ÚLTIMA MENSAGEM DO USUÁRIO: "{last_user_message}"

PROCESSO DECISÓRIO COM NORMALIZAÇÃO:

PASSO 1: IDENTIFIQUE qual campo do schema está sendo perguntado na ÚLTIMA PERGUNTA
PASSO 2: VERIFIQUE se a ÚLTIMA MENSAGEM contém informação relacionada a ESSE CAMPO
PASSO 3: SE contiver, TENTE NORMALIZAR para atender à DESCRIÇÃO e TYPE do campo
PASSO 4: EXTRAIA apenas se conseguir normalizar corretamente

NORMALIZAÇÃO INTELLIGENTE (TENTE CONVERTER QUANDO POSSÍVEL):
- Se descrição pede formato específico, tente converter da mensagem para esse formato
- Se type é "integer" ou "number", tente extrair números de qualquer representação
- Se descrição lista opções, tente mapear sinônimos ou descrições para os valores canônicos
- Se type é "array", tente identificar lista mesmo que não esteja explicitamente formatada

REGRA PRINCIPAL:
NÃO EXTRAIA se:
1. A mensagem NÃO responder à última pergunta
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
Você é um assistente que identifica campos faltantes.

Entrada:
- Schema (campos esperados): {schema}
- Dados já extraídos: {extracted}

Tarefa:
Compare os campos do schema com os dados extraídos e retorne APENAS um JSON no formato:
{{"missing": ["campo1", "campo2", ...]}}

Regras:
- Inclua campos que ainda não estão presentes nos dados já extraídos.
- Se todos os campos estão preenchidos, retorne {{"missing": []}}

Retorne apenas o JSON, sem explicações.
"""

GENERATE_QUESTION_PROMPT =  """
Você é um assistente conversacional. Sua tarefa é fazer APENAS a próxima pergunta para coletar informações que ainda faltam.

CONTEXTO:
- historico de mensagens: {context_messages}
- Campos que já foram coletados: {extracted}
- Campos que ainda faltam: {missing_fields}
- Schema com descrições: {schema}
- Última pergunta que o sistema fez: "{last_asked_question}"
- Última resposta do usuário: "{last_user_message}"

INSTRUÇÃO:
Escolha UM dos campos que faltam ({missing_fields}) e faça uma pergunta natural sobre ele, como se estivesse em uma conversa normal e AMIGÁVEL.

REGRAS:
- Use a descrição do campo no schema para saber exatamente o que perguntar
- Se for começo de conversa, inicie de forma natural (os campos que ainda faltam podem vir vazios e você pode escolher qualquer campo)
- Se já teve diálogo, continue a partir da última resposta
- Mantenha a conversa fluida

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