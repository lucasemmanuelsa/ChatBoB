import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import numpy as np

def calculate_conversational_efficiency():
    # Path to the results directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, 'resultados')
    
    # Check if directory exists
    if not os.path.exists(results_dir):
        print(f"Directory not found: {results_dir}")
        return

    # Find all conversation.json files
    conversation_files = glob.glob(os.path.join(results_dir, '*', 'conversation.json'))
    
    if not conversation_files:
        print("No conversation.json files found.")
        return

    turns_per_session = []

    print(f"Analyzing {len(conversation_files)} sessions...")

    for file_path in conversation_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Filter assistant messages
                assistant_messages = [msg for msg in data if msg.get('role') == 'assistant']
                
                count = len(assistant_messages)
                
                # Subtract the initial introductory question if there is at least one message
                # This removes the "Hello! I am ChatBoB..." message from the count
                if count > 0:
                    count -= 1
                
                turns_per_session.append(count)
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Plotting
    if not turns_per_session:
        print("No data to plot.")
        return

    # Calculate statistics
    avg_turns = np.mean(turns_per_session)
    median_turns = np.median(turns_per_session)
    min_turns = np.min(turns_per_session)
    max_turns = np.max(turns_per_session)

    print("-" * 30)
    print(f"Total Sessions Analyzed: {len(turns_per_session)}")
    print(f"Average Turns per Session: {avg_turns:.2f}")
    print(f"Median Turns per Session: {median_turns}")
    print(f"Min Turns: {min_turns}")
    print(f"Max Turns: {max_turns}")
    print("-" * 30)

    # Set Seaborn style
    sns.set_theme(style="whitegrid", palette="viridis")

    plt.figure(figsize=(14, 8))
    
    # Create the histogram using Seaborn
    # discrete=True aligns the bins to integers, which is perfect for count data
    ax = sns.histplot(turns_per_session, discrete=True, kde=True, edgecolor="black", alpha=0.7)
    
    plt.title('Eficiência Conversacional (Turnos por Sessão)', fontsize=28, fontweight='bold', pad=20)
    plt.xlabel('Número de Mensagens do Assistente (excluindo saudação)', fontsize=24)
    plt.ylabel('Frequência (Sessões)', fontsize=24)
    
    # Increase tick label size for both axes (the numbers)
    plt.tick_params(axis='both', which='major', labelsize=20)
    
    # Ensure x-axis has integer ticks for better readability
    if len(turns_per_session) > 0:
        plt.xticks(range(int(min_turns), int(max_turns) + 2))

    # Add text box with stats
    textstr = '\n'.join((
        f'Média: {avg_turns:.2f}',
        f'Mediana: {median_turns}',
        f'N: {len(turns_per_session)}'
    ))
    
    # Place a text box in upper right in axes coords
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='lightgray')
    ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    plt.tight_layout()
    output_file = 'conversational_efficiency_seaborn.png'
    plt.savefig(output_file, dpi=300)
    print(f"Histogram saved as {output_file}")
    plt.show()

if __name__ == "__main__":
    calculate_conversational_efficiency()
