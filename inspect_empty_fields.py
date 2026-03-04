import json
import os
import glob

def find_empty_fields():
    # Path to the results directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, 'resultados')
    
    # Check if directory exists
    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    # Find all finaljson.json files
    data_files = glob.glob(os.path.join(results_dir, '*', 'finaljson.json'))
    
    empty_culinarias_evitar = []
    empty_locais_favoritos = []

    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if 'data' not in content: continue
                data = content['data']
                
                # Check culinarias_evitar
                val = data.get('culinarias_evitar')
                if not val or (isinstance(val, list) and len(val) == 0):
                    empty_culinarias_evitar.append(file_path)
                
                # Check locais_favoritos
                val = data.get('locais_favoritos')
                if not val or (isinstance(val, list) and len(val) == 0):
                    empty_locais_favoritos.append(file_path)

        except Exception:
            pass

    print(f"Total sessions with empty 'culinarias_evitar': {len(empty_culinarias_evitar)}")
    print("Files (first 5):")
    for p in empty_culinarias_evitar[:5]:
        print(p)
    
    print("-" * 20)
    
    print(f"Total sessions with empty 'locais_favoritos': {len(empty_locais_favoritos)}")
    print("Files (first 5):")
    for p in empty_locais_favoritos[:5]:
        print(p)

if __name__ == "__main__":
    find_empty_fields()
