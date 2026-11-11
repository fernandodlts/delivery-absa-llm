from huggingface_hub import HfApi

api = HfApi()

MODEL_REPO = "fernandodlts/qwen2.5-3b-delivery-absa-lora"
DATASET_REPO = "fernandodlts/brazilian-delivery-absa-dataset"

MODEL_CARD = """---
language:
- pt
license: apache-2.0
tags:
- sentiment-analysis
- aspect-based-sentiment-analysis
- absa
- churn-prediction
- qwen2.5
- lora
- qlora
- unsloth
- brazilian-portuguese
datasets:
- fernandodlts/brazilian-delivery-absa-dataset
base_model: unsloth/Qwen2.5-3B-Instruct-bnb-4bit
pipeline_tag: text-generation
---

# Qwen 2.5 3B — Brazilian Food Delivery ABSA & Churn Triage (LoRA)

Fine-tuned **Qwen 2.5 3B Instruct** adapter using **QLoRA (4-bit)** and **Unsloth** for **Aspect-Based Sentiment Analysis (ABSA)** and **Customer Churn Risk Classification** on informal Brazilian Portuguese food delivery reviews.

## Task & Operational Taxonomy

Given an unstructured customer review in Brazilian Portuguese (including slang, abbreviations, and typos), the model outputs a strict JSON object with the following schema:

- **`comida`** (*Food Quality*): `positivo` | `negativo` | `neutro` | `nao_mencionado`
- **`entrega`** (*Delivery Experience*): `positivo` | `negativo` | `neutro` | `nao_mencionado`
- **`embalagem`** (*Packaging & Integrity*): `positivo` | `negativo` | `neutro` | `nao_mencionado`
- **`custo_beneficio`** (*Value for Money*): `positivo` | `negativo` | `neutro` | `nao_mencionado`
- **`risco_churn`** (*Churn Risk Alert*): `true` | `false`
- **`resumo_critica`** (*Root-Cause Summary*): Short string describing the primary operational issue, or `null` if none.

## Evaluation Results (Held-out Test Split)

Evaluated on 60 unseen test samples (`test.jsonl`) from `fernandodlts/brazilian-delivery-absa-dataset`:

| Operational Dimension | Accuracy | Correct Predictions |
| :--- | :--- | :--- |
| **Strict JSON Format Adherence** | **100.00%** | 60 / 60 |
| **Delivery (`entrega`)** | **100.00%** | 60 / 60 |
| **Churn Risk (`risco_churn`)** | **98.33%** | 59 / 60 |
| **Packaging (`embalagem`)** | **90.00%** | 54 / 60 |
| **Food Quality (`comida`)** | **85.00%** | 51 / 60 |
| **Value for Money (`custo_beneficio`)** | **81.67%** | 49 / 60 |
| **Mean Operational Accuracy** | **91.00%** | — |

## Training Hyperparameters

- **Base Model:** `unsloth/Qwen2.5-3B-Instruct-bnb-4bit`
- **PEFT Method:** QLoRA (`r=16`, `lora_alpha=16`, `lora_dropout=0`)
- **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
- **Optimizer:** `adamw_8bit`
- **Learning Rate:** `2e-4` (Linear scheduler)
- **Batch Size:** `2` per device (`gradient_accumulation_steps=4`, effective batch size = `8`)
- **Epochs:** `3` (90 steps across 240 training examples)

## Quickstart (Inference)

~~~python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model_id = "Qwen/Qwen2.5-3B-Instruct"
adapter_id = "fernandodlts/qwen2.5-3b-delivery-absa-lora"

tokenizer = AutoTokenizer.from_pretrained(adapter_id)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, adapter_id)

system_prompt = (
    "Você é um especialista em análise de sentimento e extração de dados operacionais do setor de delivery (iFood).\\n"
    "Sua tarefa é analisar avaliações de clientes e extrair um objeto JSON estrito com os seguintes aspectos:\\n"
    "- comida: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\\n"
    "- entrega: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\\n"
    "- embalagem: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\\n"
    "- custo_beneficio: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\\n"
    "- risco_churn: true ou false\\n"
    "- resumo_critica: frase curta com o problema principal ou null se não houver problemas.\\n\\n"
    "Responda APENAS com o JSON válido, sem introduções ou explicações."
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "o burger tava surreal de bom mas atrasou 1h e esqueceram meu refri nunca mais peco"}
]

inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

outputs = model.generate(inputs, max_new_tokens=256, temperature=0.1)
print(tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True))
~~~
"""

DATASET_CARD = """---
language:
- pt
license: apache-2.0
task_categories:
- text-classification
- text-generation
tags:
- absa
- sentiment-analysis
- food-delivery
- brazilian-portuguese
- synthetic-data
size_categories:
- n<1K
---

# Brazilian Food Delivery ABSA & Churn Dataset

Synthetic dataset formatted in **ChatML (`train.jsonl` / `test.jsonl`)** for Supervised Fine-Tuning (SFT) of Large Language Models on **Aspect-Based Sentiment Analysis (ABSA)** and **Customer Churn Detection** within the Brazilian food delivery ecosystem.

## Dataset Structure

- **Total Samples:** 300 Pydantic-validated examples across 12 realistic operational scenarios.
- **Train Split (`train.jsonl`):** 240 examples (80%)
- **Test Split (`test.jsonl`):** 60 examples (20%)
- **Domain Nuances:** Captures informal Brazilian Portuguese, mobile keyboard typos, regional slang, kitchen accuracy failures, packaging issues, and portion-to-price complaints.
"""

print(f"Publicando Model Card em {MODEL_REPO}...")
api.upload_file(
    path_or_fileobj=MODEL_CARD.encode("utf-8"),
    path_in_repo="README.md",
    repo_id=MODEL_REPO,
    repo_type="model"
)

print(f"Publicando Dataset Card em {DATASET_REPO}...")
api.upload_file(
    path_or_fileobj=DATASET_CARD.encode("utf-8"),
    path_in_repo="README.md",
    repo_id=DATASET_REPO,
    repo_type="dataset"
)

print("\nDocumentação publicada com sucesso nos dois repositórios!")