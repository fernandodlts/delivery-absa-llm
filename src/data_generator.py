import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

from schemas import ExemploTreinamento

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada no ficheiro .env!")

client = genai.Client(api_key=api_key)

class LoteTreinamento(BaseModel):
    exemplos: list[ExemploTreinamento]

CENARIOS = [
    # 1. Cozinha & Sabor
    "Comida espetacular: saborosa, bem temperada, ingredientes frescos e no ponto perfeito. Não menciona a entrega.",
    # 2. Acurácia de Pedido / Erro de Cozinha
    "Restaurante ignorou totalmente as observações (ex: mandou cebola/molho quando foi pedido sem) ou faltou um item pago do combo.",
    # 3. Custo-Benefício Péssimo
    "Preço abusivo para uma porção minúscula/miserável. Cliente se sentiu enganado pela foto do cardápio vs a realidade.",
    # 4. Custo-Benefício Excelente
    "Preço muito justo e porção generosa/farta. Prato bem servido que alimenta muito bem pelo valor pago.",
    # 5. Embalagem e Higiene
    "Embalagem sem lacre de segurança ou comida chegou toda revirada/misturada dentro do pote por falta de divisória adequada.",
    # 6. Alimento Cru/Estragado (Risco Alto de Churn)
    "Comida azeda, estragada, fria ou carne crua. Cliente furioso ameaçando Procon, pedindo estorno no app e prometendo nunca mais pedir.",
    # 7. Textura / Degradação no Transporte
    "Alimento que degradou na viagem (batata frita muito murcha, casquinha ensopada pelo vapor, pizza grudada na tampa).",
    # 8. Avaliação Mista Típica
    "O prato estava uma delícia e quentinho, mas o tempo de espera no app foi absurdo (mais de 1h de atraso total).",
    # 9. Gírias Informais / Review Curto
    "Review muito curto, elogioso ou neutro, usando gírias brasileiras de aplicativo (ex: 'rango brabo dms', 'salvou o almoço', 'top').",
    # 10. Review Confuso / Sem Pontuação
    "Review confuso, com erros grotescos de digitação de teclado de celular, sem pontuação ou emojis misturados sem texto claro.",
    # 11. Embalagem Perfeita e Lacre Intacto
    "Embalagem térmica exemplar, comida fumegando de quente, sacola lacrada com selo de segurança intacto.",
    # 12. Padrão Neutro / Indiferente
    "Avaliação padrão e morna: nada de especial, comida ok mas sem sal, entrega no limite do tempo previsto, nota mediana."
]

ERROS_TRANSITORIOS = ("500", "503", "429", "INTERNAL", "UNAVAILABLE", "RESOURCE_EXHAUSTED")
EXEMPLOS_POR_CENARIO = 25

def gerar_lote_resiliente(cenario: str, quantidade: int = EXEMPLOS_POR_CENARIO, max_tentativas: int = 5) -> list[dict]:
    prompt = f"""
    Você é um engenheiro de IA criando dados de treino de alta fidelidade para o sistema de recomendação e qualidade do iFood.
    Gere exatamente {quantidade} avaliações reais e orgânicas de clientes de aplicativo de delivery em português do Brasil.

    Cenário operacional a reproduzir:
    "{cenario}"

    Diretrizes cruciais de distribuição:
    - O foco deve ser o RESTAURANTE, a COMIDA e a EXPERIÊNCIA DO PEDIDO.
    - NÃO force a figura do motoboy em todas as avaliações. Foque no prato, no preço, na precisão da cozinha ou em itens em falta.
    - Varie o tom: gírias (podrão, top, monstro, rango), linguagem truncada de teclado touch (vc, pq, mt, sem pontuação), ironia ou frustração.
    - Se a entrega não for mencionada no texto, classifique 'entrega' estritamente como 'nao_mencionado'.
    - Marque 'risco_churn' como True apenas em falhas críticas (comida estragada, estorno exigido, cancelamento de conta).
    """

    for tentativa in range(1, max_tentativas + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LoteTreinamento,
                    temperature=1.0
                ),
            )
            lote_validado = LoteTreinamento.model_validate_json(response.text)
            return [item.model_dump() for item in lote_validado.exemplos]

        except Exception as e:
            msg = str(e)
            if any(cod in msg for cod in ERROS_TRANSITORIOS) and tentativa < max_tentativas:
                espera = tentativa * 6  # 6s, 12s, 18s, 24s
                print(f"      [Tentativa {tentativa}/{max_tentativas}] Servidor ocupado. Aguardando {espera}s para retomar...")
                time.sleep(espera)
            else:
                raise e

def main():
    arquivo_saida = Path("data/raw_synthetic.json")
    todos_exemplos = []

    # Carrega o ficheiro existente se houver
    if arquivo_saida.exists():
        with open(arquivo_saida, "r", encoding="utf-8") as f:
            todos_exemplos = json.load(f)

    cenarios_concluidos = len(todos_exemplos) // EXEMPLOS_POR_CENARIO
    print(f"Ponto de controlo: {len(todos_exemplos)} exemplos encontrados ({cenarios_concluidos}/{len(CENARIOS)} cenários já concluídos).")

    if cenarios_concluidos >= len(CENARIOS):
        print("Todos os cenários já foram concluídos! O dataset está completo.")
        return

    # Itera apenas sobre os cenários que ainda faltam gerar
    for indice in range(cenarios_concluidos, len(CENARIOS)):
        cenario = CENARIOS[indice]
        numero_cenario = indice + 1
        print(f"[{numero_cenario}/{len(CENARIOS)}] Processando cenário: {cenario[:45]}...")
        
        try:
            exemplos = gerar_lote_resiliente(cenario, quantidade=EXEMPLOS_POR_CENARIO, max_tentativas=5)
            todos_exemplos.extend(exemplos)
            
            # Persistência atómica imediata no disco
            with open(arquivo_saida, "w", encoding="utf-8") as f:
                json.dump(todos_exemplos, f, ensure_ascii=False, indent=2)
                
            print(f"   -> +{len(exemplos)} salvos no disco. Total acumulado: {len(todos_exemplos)}/300")
            time.sleep(2.5)
        except Exception as e:
            print(f"   -> Interrompido no cenário {numero_cenario}: {e}")
            break

    print(f"\nEstado final: {len(todos_exemplos)} exemplos preservados no ficheiro: {arquivo_saida}")

if __name__ == "__main__":
    main()