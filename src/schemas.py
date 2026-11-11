# src/schemas.py
from typing import Literal, Optional
from pydantic import BaseModel, Field

# Valores estritos aceitos para cada aspecto avaliado
SentimentoAspecto = Literal["positivo", "negativo", "neutro", "nao_mencionado"]

class AnaliseReviewDelivery(BaseModel):
    comida: SentimentoAspecto = Field(
        description="Sentimento quanto a sabor, temperatura, ponto do preparo ou qualidade dos ingredientes."
    )
    entrega: SentimentoAspecto = Field(
        description="Sentimento quanto ao tempo de espera, pontualidade, deslocamento ou conduta do entregador."
    )
    embalagem: SentimentoAspecto = Field(
        description="Sentimento quanto à integridade, vedação, vazamentos, sacola rasgada ou manutenção térmica."
    )
    custo_beneficio: SentimentoAspecto = Field(
        description="Sentimento quanto ao valor cobrado vs. quantidade/qualidade entregue (ex: 'caro demais', 'não vale o preço', 'muito bem servido pelo valor')."
    )
    risco_churn: bool = Field(
        description="Verdadeiro se o cliente ameaça nunca mais comprar, pede estorno explícito ou demonstra quebra total de confiança."
    )
    resumo_critica: Optional[str] = Field(
        default=None,
        description="Frase curta resumindo o principal problema operacional, se houver. Se for 100% positivo, preencher com None."
    )

class ExemploTreinamento(BaseModel):
    review_texto: str = Field(
        description="Texto simulado de uma avaliação real e informal de delivery em português."
    )
    analise: AnaliseReviewDelivery