from pathlib import Path
from huggingface_hub import HfApi

api = HfApi()

user_info = api.whoami()
hf_username = user_info["name"]

# Nome neutro, descritivo e alinhado com boas práticas de governança
DATASET_NAME = "brazilian-delivery-absa-dataset"
REPO_ID = f"{hf_username}/{DATASET_NAME}"

print(f"Identificado usuário: {hf_username}")
print(f"Criando repositório do dataset: {REPO_ID}...")

api.create_repo(
    repo_id=REPO_ID,
    repo_type="dataset",
    exist_ok=True,
    private=False
)

pasta_dados = Path("data/processed")

print("\nEnviando train.jsonl (240 exemplos)...")
api.upload_file(
    path_or_fileobj=pasta_dados / "train.jsonl",
    path_in_repo="train.jsonl",
    repo_id=REPO_ID,
    repo_type="dataset"
)

print("Enviando test.jsonl (60 exemplos)...")
api.upload_file(
    path_or_fileobj=pasta_dados / "test.jsonl",
    path_in_repo="test.jsonl",
    repo_id=REPO_ID,
    repo_type="dataset"
)

print(f"\nUpload concluído com sucesso!")
print(f"URL pública do dataset: https://huggingface.co/datasets/{REPO_ID}")