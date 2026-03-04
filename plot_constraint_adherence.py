import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import pandas as pd
import numpy as np

def calculate_constraint_adherence():
    # Path to the results directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, 'resultados')
    
    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    data_files = glob.glob(os.path.join(results_dir, '*', 'finaljson.json'))
    
    if not data_files:
        print("No finaljson.json files found.")
        return

    # Define fields to analyze and their counters
    # Adjusting based on user request:
    # 1. culinarias_preferidas (Min 2)
    # 2. culinarias_evitar (Min 1, but [] is Justified)
    # 3. locais_favoritos (Max 3)
    # 4. horario_preferido_pedido (Conditional: Only if freq >= 2)
    
    fields_to_analyze = [
        'culinarias_preferidas',
        'culinarias_evitar',
        'locais_favoritos',
        'horario_preferido_pedido' 
    ]
    
    # Structure to hold counts: Field -> Category -> Count
    stats = {field: {'Adherence': 0, 'Justified': 0, 'NonCompliance': 0} for field in fields_to_analyze}
    total_sessions = 0

    print(f"Analyzing {len(data_files)} sessions...")

    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                if 'data' not in content:
                    continue
                
                data = content['data']
                missing_fields = content.get('missing_fields', [])
                total_sessions += 1
                
                # --- Analyze 'culinarias_preferidas' ---
                # Rule: At least 2 items
                # Adherence: >= 2 items
                # NonCompliance: 1 item (system failed to insist) OR 0 items/null (failed to extract required)
                # Justified: none? Maybe if user explicitly refused repeatedly? Treating refusal as Justified.
                val = data.get('culinarias_preferidas')
                if isinstance(val, list) and len(val) >= 2:
                    stats['culinarias_preferidas']['Adherence'] += 1
                elif 'culinarias_preferidas' in missing_fields: # Explicitly marked missing/refused
                    stats['culinarias_preferidas']['Justified'] += 1
                else:
                    # < 2 items and NOT marked as missing/refused -> System failure
                    stats['culinarias_preferidas']['NonCompliance'] += 1


                # --- Analyze 'culinarias_evitar' ---
                # Rule: At least 1 item.
                # Adherence: >= 1 item
                # Justified: Only if explicitly refused/missing (in missing_fields).
                # NonCompliance: Empty list [] (System accepted "none" but rule requires min 1) or Null.
                val = data.get('culinarias_evitar')
                if isinstance(val, list) and len(val) >= 1:
                    stats['culinarias_evitar']['Adherence'] += 1
                elif 'culinarias_evitar' in missing_fields:
                     stats['culinarias_evitar']['Justified'] += 1
                else:
                     # Empty list [] or Null -> NonCompliance (Violation of Min 1 rule)
                     stats['culinarias_evitar']['NonCompliance'] += 1


                # --- Analyze 'locais_favoritos' ---
                # Rule: Max 3 items.
                # Adherence: 0 to 3 items. (Empty list is valid per user request)
                # NonCompliance: > 3 items.
                val = data.get('locais_favoritos')
                is_valid_list = isinstance(val, list)
                
                if is_valid_list:
                    if 0 <= len(val) <= 3:
                        # 0 items is valid "None", 1-3 is valid selection. All adhere to "Max 3".
                        stats['locais_favoritos']['Adherence'] += 1
                    elif len(val) > 3:
                        stats['locais_favoritos']['NonCompliance'] += 1
                elif val is None and 'locais_favoritos' in missing_fields:
                    # Explicitly missing/refused -> Justified
                    stats['locais_favoritos']['Justified'] += 1
                else:
                     # Null not in missing, or weird type
                    stats['locais_favoritos']['NonCompliance'] += 1


                # --- Analyze 'horario_preferido_pedido' ---
                # Rule: Collect ONLY IF frequencia_delivery_semanal >= 2.
                
                # Normalize frequency: handle strings, floats, ints
                raw_freq = data.get('frequencia_delivery_semanal', 0)
                freq = 0
                try:
                    if isinstance(raw_freq, (int, float)):
                        freq = float(raw_freq)
                    elif isinstance(raw_freq, str) and raw_freq.replace('.','',1).isdigit():
                        freq = float(raw_freq)
                except:
                    freq = 0 # Default to 0 if parsing fails
                
                horario = data.get('horario_preferido_pedido')
                has_horario = isinstance(horario, str) and len(horario.strip()) > 0
                
                if freq >= 2:
                    # Scenario A: High Frequency (>= 2)
                    # Requirement: Should collect.
                    if has_horario:
                        stats['horario_preferido_pedido']['Adherence'] += 1 # Success
                    elif 'horario_preferido_pedido' in missing_fields:
                        stats['horario_preferido_pedido']['Justified'] += 1 # Tried but failed/refused
                    else:
                        stats['horario_preferido_pedido']['NonCompliance'] += 1 # Failed to collect required
                else:
                    # Scenario B: Low Frequency (< 2)
                    # Requirement: Should NOT collect (Skip).
                    if not has_horario:
                        # Correctly skipped -> Adherence to negative rule
                        # User described this as "evitou corretamente perguntar".
                        # Let's map "Correctly Skipped" to Adherence? Or Justified?
                        # "Omissão Justificada" fits well: Omitted because rule said so.
                        stats['horario_preferido_pedido']['Justified'] += 1 
                    else:
                        # Collected unnecessarily -> NonCompliance (Over-collection / Rule Violation)
                        # "Perguntou indevidamente"
                        stats['horario_preferido_pedido']['NonCompliance'] += 1

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if total_sessions == 0:
        print("No valid sessions found.")
        return

    # Convert to percentages
    # Create a nice DataFrame for Seaborn
    plot_data = []
    
    for field in fields_to_analyze:
        counts = stats[field]
        # Normalize to 100% just in case of oddities, but typically sum should be total_sessions
        # But wait, missing data files might skew? No, we count per file.
        
        # Calculate percentages
        p_adhere = (counts['Adherence'] / total_sessions) * 100
        p_justified = (counts['Justified'] / total_sessions) * 100
        p_noncomp = (counts['NonCompliance'] / total_sessions) * 100
        
        plot_data.append({'Field': field, 'Category': 'Aderência Estrita', 'Percentage': p_adhere})
        plot_data.append({'Field': field, 'Category': 'Omissão Justificada', 'Percentage': p_justified})
        plot_data.append({'Field': field, 'Category': 'Não Conformidade', 'Percentage': p_noncomp})

    df = pd.DataFrame(plot_data)
    
    print("-" * 30)
    print(f"Total Sessions Analyzed: {total_sessions}")
    print(df)
    print("-" * 30)

    # Plotting
    # Stacked Bar Chart is tricky in basic Seaborn without some manual work or using histplot/displot, 
    # but barplot with 'hue' is grouped. User suggested Grouped OR Stacked. 
    # Stacked is often better for "parts of a whole (100%)".
    
    sns.set_theme(style="white", palette="muted")
    
    # Pivot for stacked plotting using pandas directly with matplotlib (easier for stacked)
    df_pivot = df.pivot(index='Field', columns='Category', values='Percentage')
    
    # Custom colors
    colors = ['#2ca02c', '#d62728', '#7f7f7f'] # Green (Adhere), Red (NonComp), Gray (Justified) - Matplotlib default-ish
    # Or specific mapping:
    category_order = ['Aderência Estrita', 'Omissão Justificada', 'Não Conformidade']
    color_map = {
        'Aderência Estrita': '#4CAF50',      # Green
        'Omissão Justificada': '#9E9E9E',    # Grey
        'Não Conformidade': '#F44336'        # Red
    }
    
    # Reorder columns
    df_pivot = df_pivot[category_order]
    
    # Enforce row order (Field order)
    df_pivot = df_pivot.reindex(fields_to_analyze)
    
    ax = df_pivot.plot(kind='bar', stacked=True, figsize=(16, 16), color=[color_map[c] for c in category_order], edgecolor='white', width=0.7)
    
    # Increased padding to avoid collision with top legend
    plt.title('Taxa de Aderência às Regras', fontsize=32, fontweight='bold', pad=80)
    plt.xlabel('Campos com Regras Específicas', fontsize=28, fontweight='bold')
    plt.ylabel('Porcentagem de Sessões (%)', fontsize=28, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=28)
    plt.yticks(fontsize=28)
    plt.ylim(0, 105)
    
    # Legend at the top, centered, horizontal
    plt.legend(
        title='', 
        fontsize=24, 
        loc='lower center', 
        bbox_to_anchor=(0.5, 1.02), 
        ncol=3,
        frameon=False
    )
    
    # Add percentage labels
    for c in ax.containers:
        # custom label calculation
        labels = [f'{v.get_height():.1f}%' if v.get_height() > 5 else '' for v in c]
        ax.bar_label(c, labels=labels, label_type='center', fontsize=28, color='white', fontweight='bold')

    plt.tight_layout()
    output_file = 'constraint_adherence_stacked.png'
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    calculate_constraint_adherence()
