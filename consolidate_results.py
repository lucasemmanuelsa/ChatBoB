import os
import json

def format_json(data):
    """Formata o JSON para string bonita."""
    return json.dumps(data, indent=4, ensure_ascii=False)

def consolidate_results():
    base_dir = "resultados"
    output_file = "consolidado_geral.txt"
    
    if not os.path.exists(base_dir):
        print(f"❌ Diretório '{base_dir}' não encontrado.")
        print("💡 Dica: Execute primeiro o script 'download_s3_results.py' para baixar os dados.")
        return

    print(f"📂 Lendo arquivos de '{base_dir}'...")
    
    sessions_found = 0
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("=================================================================\n")
        outfile.write("       RELATÓRIO CONSOLIDADO DE EXECUÇÕES DO CHATBOT TCC\n")
        outfile.write("=================================================================\n\n")

        # Percorre a pasta resultados para encontrar as pastas de sessão
        # A estrutura esperada é: resultados/session_XXXX/... ou resultados/conversation_logs/session_XXXX/...
        # O script de download preserva a estrutura do S3. No S3, parece ser conversation_logs/session_...
        
        for root, dirs, files in os.walk(base_dir):
            # Verifica se estamos numa pasta de sessão (contém conversation.json)
            if "conversation.json" in files and "finaljson.json" in files:
                folder_name = os.path.basename(root)
                sessions_found += 1
                
                print(f"📝 Processando sessão: {folder_name}")
                
                outfile.write(f"SESSION ID: {folder_name}\n")
                outfile.write("-" * 50 + "\n")
                
                # 1. Processar conversation.json
                conv_path = os.path.join(root, "conversation.json")
                try:
                    with open(conv_path, "r", encoding="utf-8") as f:
                        conv_data = json.load(f)
                    
                    outfile.write(">>> CONVERSATION HISTORY:\n")
                    
                    # Se for uma lista de mensagens (formato usual do LangChain/Streamlit)
                    if isinstance(conv_data, list):
                        for msg in conv_data:
                            role = msg.get("type") or msg.get("role", "unknown")
                            content = msg.get("content", "")
                            outfile.write(f"[{role.upper()}]: {content}\n")
                    else:
                        # Fallback se não for lista
                        outfile.write(format_json(conv_data) + "\n")
                        
                except Exception as e:
                    outfile.write(f"[ERRO AO LER CONVERSATION.JSON]: {str(e)}\n")
                
                outfile.write("\n")
                
                # 2. Processar finaljson.json
                final_path = os.path.join(root, "finaljson.json")
                try:
                    with open(final_path, "r", encoding="utf-8") as f:
                        final_data = json.load(f)
                    
                    outfile.write(">>> EXTRACTION RESULT (JSON):\n")
                    outfile.write(format_json(final_data))
                    outfile.write("\n")
                except Exception as e:
                    outfile.write(f"[ERRO AO LER FINALJSON.JSON]: {str(e)}\n")
                
                outfile.write("\n" + ("=" * 80) + "\n\n")

    print(f"\n✅ Concluído! {sessions_found} sessões consolidadas em '{output_file}'.")

if __name__ == "__main__":
    consolidate_results()
