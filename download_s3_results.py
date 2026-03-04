import os
import boto3
try:
    import toml
except ImportError:
    import sys
    print("❌ O pacote 'toml' é necessário para ler os segredos.")
    print("👉 Instale com: pip install toml")
    sys.exit(1)
from pathlib import Path

def load_secrets():
    """
    Carrega segredos do arquivo .streamlit/secrets.toml ou variáveis de ambiente.
    """
    secrets_path = Path(".streamlit/secrets.toml")
    secrets = {}
    
    # 1. Tenta ler o arquivo TOML diretamente
    if secrets_path.exists():
        try:
            secrets = toml.load(secrets_path)
            print("✅ Configurações carregadas de .streamlit/secrets.toml")
        except Exception as e:
            print(f"⚠️ Erro ao ler .streamlit/secrets.toml: {e}")
    
    # 2. Se não achou, tenta variáveis de ambiente (fallback)
    if not secrets:
        # Tenta carregar do .env se existir
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        secrets = os.environ
        
    return secrets

def get_secret(secrets, key, default=None):
    """Recupera valor do dicionário de segredos ou env var."""
    # Tenta acesso direto
    if key in secrets:
        return secrets[key]
    
    # Tenta acesso aninhado (ex: [aws] access_key) se a estrutura for complexa, 
    # mas aqui assumimos estrutura plana conforme uso anterior.
    
    return os.getenv(key, default)

def download_s3_bucket():
    secrets = load_secrets()
    
    # Carrega configurações
    bucket_name = get_secret(secrets, "S3_BUCKET_NAME")
    aws_region = get_secret(secrets, "AWS_REGION", "us-east-2")
    aws_access_key = get_secret(secrets, "AWS_ACCESS_KEY_ID")
    aws_secret_key = get_secret(secrets, "AWS_SECRET_ACCESS_KEY")

    if not bucket_name or not aws_access_key or not aws_secret_key:
        print("❌ Erro: Credenciais AWS ou S3_BUCKET_NAME não encontradas.")
        print("Verifique .streamlit/secrets.toml ou .env")
        return

    print(f"🔌 Conectando ao S3... Bucket: {bucket_name}")

    try:
        s3 = boto3.client(
            's3',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return

    # Diretório local de destino
    dest_dir = "resultados"
    os.makedirs(dest_dir, exist_ok=True)

    print("📦 Listando objetos...")
    
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name)

    count = 0
    for page in pages:
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            key = obj['Key']
            
            # Ignora pastas (se a key terminar com /)
            if key.endswith('/'):
                continue
                
            local_path = os.path.join(dest_dir, key)
            local_folder = os.path.dirname(local_path)
            
            # Cria a pasta local se não existir
            os.makedirs(local_folder, exist_ok=True)
            
            print(f"⬇️  Baixando: {key} -> {local_path}")
            try:
                s3.download_file(bucket_name, key, local_path)
                count += 1
            except Exception as e:
                print(f"   ⚠️ Falha ao baixar {key}: {e}")

    print(f"\n✅ Concluído! total de {count} arquivos baixados em '{dest_dir}/'.")

if __name__ == "__main__":
    download_s3_bucket()
