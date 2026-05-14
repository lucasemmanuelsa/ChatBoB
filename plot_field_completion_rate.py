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

    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    data_files = glob.glob(os.path.join(results_dir, '*', 'finaljson.json'))

    if not data_files:
        print("No finaljson.json files found.")
        return

    field_counts = {}
    total_sessions = 0

    # Field label translations
    field_labels = {
        'culinarias_preferidas': 'Preferred Cuisines',
        'culinarias_evitar': 'Cuisines to Avoid',
        'locais_favoritos': 'Favorite Locations',
        'horario_preferido_pedido': 'Preferred Order Time',
        'frequencia_delivery_semanal': 'Weekly Delivery Frequency',
        'endereco_entrega': 'Delivery Address'
    }

    print(f"Analyzing {len(data_files)} sessions...")

    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

                if 'data' not in content:
                    print(f"Skipping {file_path}: 'data' key missing")
                    continue

                data = content['data']
                total_sessions += 1

                for key, value in data.items():
                    if key not in field_counts:
                        field_counts[key] = 0

                    # Count as success if field exists and value is not None
                    if value is not None:
                        field_counts[key] += 1

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if total_sessions == 0:
        print("No valid sessions found.")
        return

    # Convert to percentages
    field_percentages = {
        field_labels.get(k, k): (v / total_sessions) * 100
        for k, v in field_counts.items()
    }

    # Create dataframe
    df = pd.DataFrame(
        list(field_percentages.items()),
        columns=['Field', 'Completion Rate (%)']
    )

    df = df.sort_values(
        by='Completion Rate (%)',
        ascending=False
    )

    print("-" * 30)
    print(f"Total Sessions Analyzed: {total_sessions}")
    print("Completion Rates:")
    print(df)
    print("-" * 30)

    # Plot style
    sns.set_theme(style="whitegrid", palette="viridis")

    plt.figure(figsize=(16, 10))

    ax = sns.barplot(
        x='Completion Rate (%)',
        y='Field',
        data=df,
        hue='Field',
        legend=False,
        palette='viridis'
    )

    plt.title(
        'Field Completion Rate',
        fontsize=32,
        fontweight='bold',
        pad=30
    )

    plt.xlabel(
        'Success Rate (%)',
        fontsize=32,
        fontweight='bold'
    )

    plt.ylabel('')

    plt.xlim(0, 130)

    plt.tick_params(
        axis='both',
        which='major',
        labelsize=28
    )

    # Add labels on bars
    for p in ax.patches:
        width = p.get_width()

        plt.text(
            width + 1.5,
            p.get_y() + p.get_height() / 2,
            f'{width:.1f}%',
            va='center',
            fontsize=26,
            fontweight='bold',
            color='black'
        )

    # Add total sessions box
    plt.text(
        0.95,
        0.05,
        f'Total Sessions: {total_sessions}',
        transform=plt.gca().transAxes,
        fontsize=28,
        verticalalignment='bottom',
        horizontalalignment='right',
        bbox=dict(
            boxstyle='round',
            facecolor='white',
            alpha=0.8,
            edgecolor='lightgray'
        )
    )

    plt.tight_layout()

    output_file = 'field_completion_rate_en.png'
    plt.savefig(output_file, dpi=300)

    print(f"Chart saved as {output_file}")
    plt.show()


if __name__ == "__main__":
    calculate_field_completion_rate()