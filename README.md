# Chat Data Extractor

Intelligent agent for structured data extraction from chat conversations. 
Converts natural dialogue into structured JSON using schemas for databases, forms, and APIs.

## Features
- Dynamic schema-based extraction
- Multi-destination support (SQL, NoSQL, Forms)
- Context-aware data capture
- JSON validation and structuring
- Easy integration

## How It Works

### 1. Define Your Schema
Create a JSON schema defining the fields you want to extract:

```json
{
  "generos_musicais_favoritos": {
    "description": "dois ou mais gêneros musicais que o usuário mais aprecia e costuma ouvir com maior frequência",
    "type": "List",
    "required": true
  },
  "generos_musicais_avessos": {
    "description": "Um ou mais gêneros musicais que o usuário menos gosta de ouvir, sendo normalmente sua última opção de escolha",
    "type": "List",
    "required": true
  },
  "artistas_favoritos": {
    "description": "Um ou mais artistas preferidos do usuário, cujas músicas ele costuma ouvir com mais frequência",
    "type": "List",
    "required": true
  },
  "musicas_favoritas": {
    "description": "Até cinco músicas favoritas do usuário, as quais ele costuma ouvir com mais frequência",
    "type": "List",
    "required": false
  }
}
```

### 2. Natural Conversation
The agent conducts a natural conversation to collect the required information:

```
Agent: Olá! Para começarmos: qual é o seu nome?
User: Meu nome é Lucas!

Agent: Lucas, quais são seus gêneros musicais favoritos?
User: Gosto de rock e pop

Agent: E quais gêneros você menos gosta?
User: Não curto muito sertanejo

Agent: Quais são seus artistas favoritos?
User: Metallica é meu favorito
```

### 3. Structured Output
The agent automatically extracts and structures the data into JSON:

```json
{
  "metadata": {
    "created_at": "2024-01-31T22:27:56Z",
    "source": "user_input",
    "schema_version": "1.0"
  },
  "data": {
    "generos_musicais_favoritos": ["rock", "pop"],
    "generos_musicais_avessos": ["sertanejo"],
    "artistas_favoritos": ["metallica"],
    "musicas_favoritas": ["money"]
  },
  "missing_fields": []
}
```

## Field Properties

- **description**: Detailed description for the agent to understand what to extract
- **type**: Data type (String, Number, List, Boolean)
- **required**: Whether the field is mandatory (true/false)

## Run
```bash
streamlit run demo/streamlit_app.py
```

## Features
- **Adaptive Questioning**: Adjusts strategy based on user responses
- **Data Normalization**: Automatically converts natural language to structured data
- **Validation**: Ensures extracted data matches schema requirements
- **Session Logging**: Saves conversation logs and extracted data
- **Multi-domain Support**: Works with any schema design

**Tags:** chatbot, data-extraction, json, parser, natural-language, conversation-ai, structured-data