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

    # Fields to analyze
    fields_to_analyze = [
        'culinarias_preferidas',
        'culinarias_evitar',
        'locais_favoritos',
        'horario_preferido_pedido'
    ]

    # English labels for fields
    field_labels = {
        'culinarias_preferidas': 'Preferred Cuisines',
        'culinarias_evitar': 'Cuisines to Avoid',
        'locais_favoritos': 'Favorite Locations',
        'horario_preferido_pedido': 'Preferred Order Time'
    }

    # Statistics structure
    stats = {
        field: {
            'Adherence': 0,
            'Justified': 0,
            'NonCompliance': 0
        } for field in fields_to_analyze
    }

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

                # --- Preferred Cuisines (minimum 2) ---
                val = data.get('culinarias_preferidas')
                if isinstance(val, list) and len(val) >= 2:
                    stats['culinarias_preferidas']['Adherence'] += 1
                elif 'culinarias_preferidas' in missing_fields:
                    stats['culinarias_preferidas']['Justified'] += 1
                else:
                    stats['culinarias_preferidas']['NonCompliance'] += 1

                # --- Cuisines to Avoid (minimum 1) ---
                val = data.get('culinarias_evitar')
                if isinstance(val, list) and len(val) >= 1:
                    stats['culinarias_evitar']['Adherence'] += 1
                elif 'culinarias_evitar' in missing_fields:
                    stats['culinarias_evitar']['Justified'] += 1
                else:
                    stats['culinarias_evitar']['NonCompliance'] += 1

                # --- Favorite Locations (maximum 3) ---
                val = data.get('locais_favoritos')

                if isinstance(val, list):
                    if 0 <= len(val) <= 3:
                        stats['locais_favoritos']['Adherence'] += 1
                    else:
                        stats['locais_favoritos']['NonCompliance'] += 1
                elif val is None and 'locais_favoritos' in missing_fields:
                    stats['locais_favoritos']['Justified'] += 1
                else:
                    stats['locais_favoritos']['NonCompliance'] += 1

                # --- Preferred Order Time (only if frequency >= 2) ---
                raw_freq = data.get('frequencia_delivery_semanal', 0)

                try:
                    if isinstance(raw_freq, (int, float)):
                        freq = float(raw_freq)
                    elif isinstance(raw_freq, str) and raw_freq.replace('.', '', 1).isdigit():
                        freq = float(raw_freq)
                    else:
                        freq = 0
                except:
                    freq = 0

                horario = data.get('horario_preferido_pedido')
                has_horario = isinstance(horario, str) and len(horario.strip()) > 0

                if freq >= 2:
                    if has_horario:
                        stats['horario_preferido_pedido']['Adherence'] += 1
                    elif 'horario_preferido_pedido' in missing_fields:
                        stats['horario_preferido_pedido']['Justified'] += 1
                    else:
                        stats['horario_preferido_pedido']['NonCompliance'] += 1
                else:
                    if not has_horario:
                        stats['horario_preferido_pedido']['Justified'] += 1
                    else:
                        stats['horario_preferido_pedido']['NonCompliance'] += 1

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if total_sessions == 0:
        print("No valid sessions found.")
        return

    # Convert to percentages
    plot_data = []

    for field in fields_to_analyze:
        counts = stats[field]

        p_adhere = (counts['Adherence'] / total_sessions) * 100
        p_justified = (counts['Justified'] / total_sessions) * 100
        p_noncomp = (counts['NonCompliance'] / total_sessions) * 100

        plot_data.append({
            'Field': field_labels[field],
            'Category': 'Strict Adherence',
            'Percentage': p_adhere
        })

        plot_data.append({
            'Field': field_labels[field],
            'Category': 'Justified Omission',
            'Percentage': p_justified
        })

        plot_data.append({
            'Field': field_labels[field],
            'Category': 'Non-Compliance',
            'Percentage': p_noncomp
        })

    df = pd.DataFrame(plot_data)

    print("-" * 30)
    print(f"Total Sessions Analyzed: {total_sessions}")
    print(df)
    print("-" * 30)

    # Plot
    sns.set_theme(style="white", palette="muted")

    df_pivot = df.pivot(
        index='Field',
        columns='Category',
        values='Percentage'
    )

    category_order = [
        'Strict Adherence',
        'Justified Omission',
        'Non-Compliance'
    ]

    color_map = {
        'Strict Adherence': '#4CAF50',
        'Justified Omission': '#9E9E9E',
        'Non-Compliance': '#F44336'
    }

    df_pivot = df_pivot[category_order]
    df_pivot = df_pivot.reindex(field_labels.values())

    ax = df_pivot.plot(
        kind='bar',
        stacked=True,
        figsize=(16, 16),
        color=[color_map[c] for c in category_order],
        edgecolor='white',
        width=0.7
    )

    plt.title(
        'Constraint Adherence Rate',
        fontsize=32,
        fontweight='bold',
        pad=80
    )

    plt.xlabel(
        'Fields with Specific Rules',
        fontsize=28,
        fontweight='bold'
    )

    plt.ylabel(
        'Percentage of Sessions (%)',
        fontsize=28,
        fontweight='bold'
    )

    plt.xticks(rotation=45, ha='right', fontsize=24)
    plt.yticks(fontsize=24)
    plt.ylim(0, 105)

    plt.legend(
        title='',
        fontsize=22,
        loc='lower center',
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=False
    )

    # Add percentage labels
    for c in ax.containers:
        labels = [
            f'{v.get_height():.1f}%'
            if v.get_height() > 5 else ''
            for v in c
        ]

        ax.bar_label(
            c,
            labels=labels,
            label_type='center',
            fontsize=22,
            color='white',
            fontweight='bold'
        )

    plt.tight_layout()

    output_file = 'constraint_adherence_stacked_en.png'
    plt.savefig(output_file, dpi=300)

    print(f"Chart saved as {output_file}")
    plt.show()


if __name__ == "__main__":
    calculate_constraint_adherence()