import os
import argparse
from pathlib import Path

DEFAULT_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build"
}

DEFAULT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml"
}

DELIMITER = "\n\n==================== FILE ====================\n"


def count_words(text):
    return len(text.split())


def should_include(file_path, allowed_extensions):
    return file_path.suffix.lower() in allowed_extensions


def collect_files(repo_path, allowed_extensions):
    files = []

    for root, dirs, filenames in os.walk(repo_path):
        # remove ignored dirs
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS]

        for filename in filenames:
            file_path = Path(root) / filename
            if should_include(file_path, allowed_extensions):
                files.append(file_path)

    return sorted(files)


def split_into_chunks(files, repo_path, max_words):
    chunks = []
    current_chunk = ""
    current_word_count = 0

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            continue

        relative_path = file_path.relative_to(repo_path)

        formatted_content = (
            f"{DELIMITER}"
            f"PATH: {relative_path}\n"
            f"{DELIMITER}"
            f"{content}\n"
        )

        words = count_words(formatted_content)

        if current_word_count + words > max_words:
            chunks.append(current_chunk)
            current_chunk = formatted_content
            current_word_count = words
        else:
            current_chunk += formatted_content
            current_word_count += words

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def save_chunks(chunks, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for i, chunk in enumerate(chunks, start=1):
        output_file = Path(output_dir) / f"repo_part_{i}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(chunk)

        print(f"Arquivo criado: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Converte um repositório em arquivos .txt compatíveis com NotebookLM")

    parser.add_argument("--repo_path", required=True, help="Caminho do repositório")
    parser.add_argument("--output_dir", required=True, help="Diretório de saída")
    parser.add_argument("--max_words", type=int, default=450000,
                        help="Máximo de palavras por arquivo (default: 450000)")
    parser.add_argument("--extensions", nargs="*", default=None,
                        help="Extensões permitidas (ex: .py .md .json)")

    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()

    if not repo_path.exists():
        print("Repositório não encontrado.")
        return

    allowed_extensions = set(args.extensions) if args.extensions else DEFAULT_EXTENSIONS

    print("Coletando arquivos...")
    files = collect_files(repo_path, allowed_extensions)

    print(f"{len(files)} arquivos encontrados.")

    print("Dividindo em partes...")
    chunks = split_into_chunks(files, repo_path, args.max_words)

    print(f"{len(chunks)} arquivos serão gerados.")

    print("Salvando...")
    save_chunks(chunks, args.output_dir)

    print("Concluído com sucesso.")


if __name__ == "__main__":
    main()