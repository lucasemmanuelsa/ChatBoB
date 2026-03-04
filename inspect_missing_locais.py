import json
import os
import glob

def find_missing_locais_favoritos():
    # Path to the results directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, 'resultados')
    
    # Check if directory exists
    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    # Find all finaljson.json files
    data_files = glob.glob(os.path.join(results_dir, '*', 'finaljson.json'))
    
    missing_locais = []

    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                missing_fields = content.get('missing_fields', [])
                
                if 'locais_favoritos' in missing_fields:
                    missing_locais.append(file_path)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Total sessions where 'locais_favoritos' is marked as missing: {len(missing_locais)}")
    print("Files:")
    for p in missing_locais:
        print(p)

if __name__ == "__main__":
    find_missing_locais_favoritos()
