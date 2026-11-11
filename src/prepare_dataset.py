import json
import random
from pathlib import Path

# Fixa a semente para garantir reproducibilidade exata da divisão
random.seed(42)

SYSTEM_PROMPT = """Você é um especialista em análise de sentimento e extração de dados operacionais do setor de delivery (iFood).
Sua tarefa é analisar avaliações de clientes e extrair um objeto JSON estrito com os seguintes aspectos:
- comida: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'
- entrega: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'
- embalagem: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'
- custo_beneficio: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'
- risco_churn: true ou false
- resumo_critica: frase curta com o problema principal ou null se não houver problemas.

Responda APENAS com o JSON válido, sem introduções ou explicações."""

def formatar_para_chat(exemplo: dict) -> dict:
    """Estrutura o exemplo no formato padrão de mensagens (ChatML)."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": exemplo["review_texto"]},
            {"role": "assistant", "content": json.dumps(exemplo["analise"], ensure_ascii=False)}
        ]
    }

def main():
    caminho_entrada = Path("data/raw_synthetic.json")
    if not caminho_entrada.exists():
        raise FileNotFoundError("Arquivo data/raw_synthetic.json não encontrado!")

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        dados = json.load(f)

    print(f"Total de exemplos carregados: {len(dados)}")

    # Embaralha os dados para misturar os 12 cenários
    random.shuffle(dados)

    formatados = [formatar_para_chat(item) for item in dados]

    # Split 80/20
    corte = int(len(formatados) * 0.8)
    treino = formatados[:corte]
    teste = formatados[corte:]

    pasta_saida = Path("data/processed")
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_treino = pasta_saida / "train.jsonl"
    caminho_teste = pasta_saida / "test.jsonl"

    # Salva no formato JSONL (uma linha JSON por amostra)
    with open(caminho_treino, "w", encoding="utf-8") as f:
        for item in treino:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(caminho_teste, "w", encoding="utf-8") as f:
        for item in teste:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\nProcessamento concluído:")
    print(f" - Treino: {len(treino)} exemplos em {caminho_treino}")
    print(f" - Teste:  {len(teste)} exemplos em {caminho_teste}")

if __name__ == "__main__":
    main()