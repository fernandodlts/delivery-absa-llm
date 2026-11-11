\# âš¡ Delivery Review Intelligence: ABSA \& Customer Churn Triage Engine



End-to-end AI Engineering pipeline for \*\*Aspect-Based Sentiment Analysis (ABSA)\*\* and \*\*Real-Time Customer Churn Detection\*\* in the Brazilian food delivery ecosystem. 



This project combines \*\*Supervised Fine-Tuning (SFT)\*\* of a \*\*Qwen 2.5 3B Instruct\*\* model via \*\*QLoRA (4-bit)\*\* and \*\*Unsloth\*\* with a strict \*\*Pydantic v2\*\* data contract and an interactive \*\*Streamlit\*\* triage dashboard.



\---



\## ðŸ”— Official Hugging Face Artifacts



\- \*\*Fine-Tuned LoRA Adapter:\*\* \[fernandodlts/qwen2.5-3b-delivery-absa-lora](https://huggingface.co/fernandodlts/qwen2.5-3b-delivery-absa-lora)

\- \*\*Dataset (300 Reviews â€” Train/Test Splits):\*\* \[fernandodlts/brazilian-delivery-absa-dataset](https://huggingface.co/datasets/fernandodlts/brazilian-delivery-absa-dataset)



\---



\## ðŸŽ¯ Business Problem \& Operational Taxonomy



Customer reviews in Brazilian food delivery platforms contain informal slang, mobile keyboard typos, irony, and conflicting sentiments within the same message (e.g., praising the kitchen while reporting severe delivery delays or spilled drinks). Traditional binary sentiment analysis fails to isolate which operational area caused the friction.



Given an unstructured review in Brazilian Portuguese, the engine extracts a strict JSON payload enforcing the following schema:



\- \*\*`comida`\*\* (\*Food \& Kitchen Quality\*): `positivo` | `negativo` | `neutro` | `nao\_mencionado`

\- \*\*`entrega`\*\* (\*Logistics \& Timeliness\*): `positivo` | `negativo` | `neutro` | `nao\_mencionado`

\- \*\*`embalagem`\*\* (\*Packaging \& Seal Integrity\*): `positivo` | `negativo` | `neutro` | `nao\_mencionado`

\- \*\*`custo\_beneficio`\*\* (\*Portion Size \& Value\*): `positivo` | `negativo` | `neutro` | `nao\_mencionado`

\- \*\*`risco\_churn`\*\* (\*Customer Retention Alert\*): `true` | `false`

\- \*\*`resumo\_critica`\*\* (\*Root-Cause Summary\*): Concise extraction of the primary operational failure, or `null` if none.



\---



\## ðŸ“Š Quantitative Evaluation (Held-Out Test Split)



Evaluated on \*\*60 unseen test samples\*\* (`test.jsonl`) using deterministic decoding:



| Operational Dimension | Test Accuracy | Correct Predictions |

| :--- | :--- | :--- |

| \*\*Strict JSON Schema Adherence\*\* | \*\*100.00%\*\* | 60 / 60 |

| \*\*Delivery (`entrega`)\*\* | \*\*100.00%\*\* | 60 / 60 |

| \*\*Churn Risk Detection (`risco\_churn`)\*\* | \*\*98.33%\*\* | 59 / 60 |

| \*\*Packaging (`embalagem`)\*\* | \*\*90.00%\*\* | 54 / 60 |

| \*\*Food Quality (`comida`)\*\* | \*\*85.00%\*\* | 51 / 60 |

| \*\*Value for Money (`custo\_beneficio`)\*\* | \*\*81.67%\*\* | 49 / 60 |

| \*\*Mean Operational Accuracy\*\* | \*\*91.00%\*\* | â€” |



\---



\## âš™ï¸ Fine-Tuning Architecture \& Hyperparameters



\- \*\*Base Model:\*\* `unsloth/Qwen2.5-3B-Instruct-bnb-4bit`

\- \*\*Training Dataset:\*\* 240 ChatML-formatted examples (`train.jsonl`) across 12 operational scenarios

\- \*\*PEFT Configuration:\*\* QLoRA (`r=16`, `lora\_alpha=16`, `lora\_dropout=0`)

\- \*\*Trainable Parameters:\*\* 29,933,568 / 3,115,872,256 (\*\*0.96% trained\*\*)

\- \*\*Batch Size:\*\* 2 per device (`gradient\_accumulation\_steps=4`, effective batch size = 8)

\- \*\*Training Schedule:\*\* 3 epochs (90 total steps, `adamw\_8bit` optimizer, learning rate `2e-4`)

\- \*\*Convergence:\*\* Training loss reduced from `2.0080` (Step 5) to `0.3869` (Step 90)



\---



\## ðŸ—‚ï¸ Repository Structure



\~\~\~text

delivery-absa-llm/

â”œâ”€â”€ data/

â”‚   â”œâ”€â”€ raw/                  # Raw synthetic batches validated via Pydantic

â”‚   â””â”€â”€ processed/            # ChatML train.jsonl (240) and test.jsonl (60) splits

â”œâ”€â”€ notebooks/delivery-absa-llm-notebook.ipynb  # Google Colab QLoRA training \& evaluation notebook

â”œâ”€â”€ src/

â”‚   â”œâ”€â”€ schemas.py            # Pydantic v2 data contract \& taxonomy definitions

â”‚   â”œâ”€â”€ generate\_dataset.py   # Synthetic dataset generator with domain scenarios

â”‚   â”œâ”€â”€ format\_dataset.py     # ChatML converter and stratified train/test splitter

â”‚   â”œâ”€â”€ upload\_dataset.py     # Hugging Face Hub dataset publisher

â”‚   â”œâ”€â”€ publish\_docs.py       # Automated Model Card \& Dataset Card publisher

â”‚   â””â”€â”€ app.py                # Interactive Streamlit ABSA \& Churn Triage Dashboard

â”œâ”€â”€ .gitignore

â”œâ”€â”€ requirements.txt

â””â”€â”€ README.md

\~\~\~



\---



\## ðŸš€ Running the Interactive Triage Dashboard Locally



1\. \*\*Clone the repository and activate the virtual environment:\*\*

\~\~\~bash

git clone https://github.com/ YOUR\_USERNAME /delivery-absa-llm.git

cd delivery-absa-llm

python -m venv .venv

.\\.venv\\Scripts\\activate

pip install -r requirements.txt

\~\~\~



2\. \*\*Configure your API key in a `.env` file at the project root:\*\*

\~\~\~env

GEMINI\_API\_KEY=your\_api\_key\_here

\~\~\~



3\. \*\*Launch the Streamlit application:\*\*

\~\~\~bash

streamlit run src/app.py

\~\~\~


