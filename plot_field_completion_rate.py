import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import pandas as pd

def calculate_field_completion_rate():
    # Path to the results directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, 'resultados')
    
    # Check if directory exists
    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    # Find all finaljson.json files
    data_files = glob.glob(os.path.join(results_dir, '*', 'finaljson.json'))
    
    if not data_files:
        print("No finaljson.json files found.")
        return

    field_counts = {}
    total_sessions = 0

    print(f"Analyzing {len(data_files)} sessions...")

    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                # Check if 'data' key exists
                if 'data' not in content:
                    print(f"Skipping {file_path}: 'data' key missing")
                    continue
                
                data = content['data']
                total_sessions += 1
                
# Get fields that the system explicitly marked as missing (if available)
                missing_fields = content.get('missing_fields', [])
                
                # Iterate over all keys in the data dictionary
                for key, value in data.items():
                    if key not in field_counts:
                        field_counts[key] = 0
                    
                    # Logic: 
                    # 1. If key is NOT in missing_fields, it's a success.
                    # 2. If key IS in missing_fields, but the extracted value is populated (not None),
                    #    we treat it as a success (inconsistency in the extractor).
                    # 3. If key IS in missing_fields and value is empty (e.g. empty list),
                    #    we treat it as success per user request (empty = "none" = success).
                    #    This effectively ignores missing_fields for specific keys if the user considers "vazio" as success.
                    
                    # Essentially, we are being very lenient:
                    # If the key exists in the data structure, we count it as success, 
                    # UNLESS the value is explicitly None (and even then, maybe valid?).
                    # But sticking to previous logic: trust data content over missing_fields tag.
                    
                    # Refined Logic:
                    # If the data has a value (even empty list or string), count as success.
                    # Only count as failure if the key is missing entirely from data dict or value is None.
                    
                    is_success = False
                    
                    if value is not None:
                         is_success = True
                    
                    if is_success:
                        field_counts[key] += 1
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if total_sessions == 0:
        print("No valid sessions found.")
        return

    # Calculate percentages
    field_percentages = {k: (v / total_sessions) * 100 for k, v in field_counts.items()}
    
    # Create DataFrame for plotting
    df = pd.DataFrame(list(field_percentages.items()), columns=['Campo', 'Taxa de Conclusão (%)'])
    df = df.sort_values(by='Taxa de Conclusão (%)', ascending=False)

    print("-" * 30)
    print(f"Total Sessions Analyzed: {total_sessions}")
    print("Completion Rates:")
    print(df)
    print("-" * 30)

    # Set Seaborn style
    sns.set_theme(style="whitegrid", palette="viridis")

    plt.figure(figsize=(16, 10))
    
    # Create the bar chart
    ax = sns.barplot(x='Taxa de Conclusão (%)', y='Campo', data=df, hue='Campo', legend=False, palette='viridis')
    
    plt.title('Taxa de Conclusão de Campos', fontsize=32, fontweight='bold', pad=30)
    plt.xlabel('Taxa de Sucesso (%)', fontsize=32, fontweight='bold')
    plt.ylabel('', fontsize=32, fontweight='bold') # Remove Y label to save space
    plt.xlim(0, 130) # Add even more space for labels
    
    # Increase tick label size significantly
    plt.tick_params(axis='both', which='major', labelsize=28)
    
    # Add percentage labels to the end of each bar
    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 1.5, p.get_y() + p.get_height()/2, 
                 f'{width:.1f}%', 
                 va='center', fontsize=26, fontweight='bold', color='black')

    # Add text box with N
    plt.text(0.95, 0.05, f'Total de Sessões: {total_sessions}', 
             transform=plt.gca().transAxes, fontsize=28,
             verticalalignment='bottom', horizontalalignment='right', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='lightgray'))

    plt.tight_layout()
    output_file = 'field_completion_rate_seaborn.png'
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    calculate_field_completion_rate()
