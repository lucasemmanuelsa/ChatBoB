import json

class Schema:
    def __init__(self, schema_dict: dict):
        # Usa o JSON exatamente como foi carregado; não exige chave "fields".
        self.fields = schema_dict

    @staticmethod
    def load_from_file(path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Schema(data)
    
"""
# Criar schema diretamente
schema1 = Schema({"fields": {"nome": "string", "idade": "number"}})

# Criar schema a partir de arquivo
schema2 = Schema.load_from_file("meu_esquema.json")
"""