import os
import time
from typing import Literal, Optional
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()


class AnaliseAspectos(BaseModel):
    comida: Literal["positivo", "negativo", "neutro", "nao_mencionado"]
    entrega: Literal["positivo", "negativo", "neutro", "nao_mencionado"]
    embalagem: Literal["positivo", "negativo", "neutro", "nao_mencionado"]
    custo_beneficio: Literal["positivo", "negativo", "neutro", "nao_mencionado"]
    risco_churn: bool
    resumo_critica: Optional[str] = None


st.set_page_config(
    page_title="Delivery Intelligence • ABSA Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS_MODERNO = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');"
    "html, body, [class*='css'] { font-family: 'Plus Jakarta Sans', sans-serif !important; }"
    "header[data-testid='stHeader'] { background: transparent !important; }"
    ".stApp { background: radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%), radial-gradient(circle at 85% 20%, rgba(244, 63, 94, 0.10) 0%, transparent 45%), #090C15; }"
    ".block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1240px; }"
    "@keyframes fadeInUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }"
    "@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.35); opacity: 0.65; } }"
    "@keyframes shimmer { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }"
    "[data-testid='stSidebar'] { background: rgba(13, 17, 28, 0.85) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 255, 255, 0.06); }"
    ".hero-wrapper { position: relative; background: linear-gradient(135deg, rgba(22, 28, 45, 0.78) 0%, rgba(15, 19, 32, 0.88) 100%); backdrop-filter: blur(18px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; padding: 32px 36px; margin-bottom: 28px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45); animation: fadeInUp 0.5s ease-out; }"
    ".status-pill { display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35); color: #A5B4FC; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 14px; }"
    ".live-dot { width: 8px; height: 8px; background-color: #10B981; border-radius: 50%; box-shadow: 0 0 10px #10B981; animation: pulseDot 2s infinite ease-in-out; }"
    ".hero-title { font-size: 34px; font-weight: 800; letter-spacing: -0.6px; margin: 0 0 8px 0; background: linear-gradient(90deg, #FFFFFF 0%, #CBD5E1 50%, #F43F5E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }"
    ".hero-subtitle { font-size: 15.5px; color: #94A3B8; line-height: 1.5; margin: 0; max-width: 820px; }"
    "div.stButton > button { border-radius: 14px !important; font-weight: 600 !important; font-size: 14px !important; padding: 10px 18px !important; transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; background: rgba(22, 28, 45, 0.75) !important; color: #E2E8F0 !important; }"
    "div.stButton > button:hover { transform: translateY(-3px) !important; border-color: rgba(99, 102, 241, 0.55) !important; background: rgba(30, 41, 69, 0.9) !important; box-shadow: 0 10px 24px -6px rgba(99, 102, 241, 0.35) !important; color: #FFFFFF !important; }"
    "div.stButton > button:active { transform: translateY(0px) scale(0.98) !important; }"
    "div.stButton > button[kind='primary'] { background: linear-gradient(135deg, #FF3B5C 0%, #FF6B2B 50%, #6366F1 100%) !important; background-size: 200% 200% !important; animation: shimmer 6s ease infinite !important; border: none !important; color: #FFFFFF !important; font-size: 15.5px !important; font-weight: 700 !important; padding: 14px 24px !important; border-radius: 16px !important; box-shadow: 0 10px 30px -6px rgba(255, 59, 92, 0.5) !important; }"
    "div.stButton > button[kind='primary']:hover { transform: translateY(-3px) scale(1.005) !important; box-shadow: 0 16px 36px -6px rgba(255, 59, 92, 0.7) !important; }"
    "div[data-testid='stTextArea'] textarea { background: rgba(15, 20, 34, 0.85) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 18px !important; padding: 16px !important; font-size: 15px !important; color: #F8FAFC !important; transition: all 0.25s ease !important; box-shadow: inset 0 2px 6px rgba(0,0,0,0.3) !important; }"
    "div[data-testid='stTextArea'] textarea:focus { border-color: #6366F1 !important; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.22), inset 0 2px 6px rgba(0,0,0,0.3) !important; }"
    ".aspect-card { position: relative; border-radius: 20px; padding: 22px 18px; text-align: center; transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1); backdrop-filter: blur(16px); margin-bottom: 14px; animation: fadeInUp 0.55s ease-out; }"
    ".aspect-card:hover { transform: translateY(-6px); }"
    ".card-positivo { background: linear-gradient(180deg, rgba(16, 185, 129, 0.14) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 12px 30px -10px rgba(16, 185, 129, 0.25); }"
    ".card-negativo { background: linear-gradient(180deg, rgba(244, 63, 94, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(244, 63, 94, 0.45); box-shadow: 0 12px 30px -10px rgba(244, 63, 94, 0.28); }"
    ".card-neutro { background: linear-gradient(180deg, rgba(245, 158, 11, 0.14) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(245, 158, 11, 0.4); box-shadow: 0 12px 30px -10px rgba(245, 158, 11, 0.22); }"
    ".card-nao_mencionado { background: rgba(15, 20, 34, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); opacity: 0.78; }"
    ".icon-circle { width: 52px; height: 52px; margin: 0 auto 12px auto; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 26px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); }"
    ".aspect-title { color: #CBD5E1; font-size: 13px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 10px; }"
    ".pill-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 999px; font-weight: 700; font-size: 12.5px; letter-spacing: 0.4px; }"
    ".pill-positivo { background: rgba(16, 185, 129, 0.18); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.35); }"
    ".pill-negativo { background: rgba(244, 63, 94, 0.18); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.35); }"
    ".pill-neutro { background: rgba(245, 158, 11, 0.18); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.35); }"
    ".pill-nao_mencionado { background: rgba(255, 255, 255, 0.05); color: #64748B; border: 1px solid rgba(255, 255, 255, 0.08); }"
    ".banner-churn { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; background: linear-gradient(90deg, rgba(244, 63, 94, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%); border: 1px solid rgba(244, 63, 94, 0.45); border-left: 6px solid #F43F5E; padding: 20px 26px; border-radius: 18px; margin-bottom: 24px; box-shadow: 0 14px 35px -8px rgba(244, 63, 94, 0.3); animation: fadeInUp 0.4s ease-out; }"
    ".banner-stable { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; background: linear-gradient(90deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.92) 100%); border: 1px solid rgba(16, 185, 129, 0.45); border-left: 6px solid #10B981; padding: 20px 26px; border-radius: 18px; margin-bottom: 24px; box-shadow: 0 14px 35px -8px rgba(16, 185, 129, 0.25); animation: fadeInUp 0.4s ease-out; }"
    ".telemetry-chip { font-family: 'JetBrains Mono', monospace; font-size: 12px; background: rgba(0, 0, 0, 0.35); border: 1px solid rgba(255, 255, 255, 0.1); color: #E2E8F0; padding: 6px 12px; border-radius: 10px; }"
    ".glass-panel { background: rgba(15, 21, 36, 0.78); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 24px; margin-top: 6px; animation: fadeInUp 0.65s ease-out; }"
    ".action-item { display: flex; align-items: center; gap: 12px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 12px 16px; margin-top: 10px; font-size: 14px; color: #E2E8F0; transition: all 0.2s ease; }"
    ".action-item:hover { background: rgba(255, 255, 255, 0.06); transform: translateX(4px); border-color: rgba(99, 102, 241, 0.4); }"
    ".metric-row { margin-bottom: 14px; }"
    ".metric-head { display: flex; justify-content: space-between; font-size: 13px; color: #CBD5E1; font-weight: 600; margin-bottom: 5px; }"
    ".bar-bg { width: 100%; height: 7px; background: rgba(255, 255, 255, 0.07); border-radius: 99px; overflow: hidden; }"
    ".bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #6366F1 0%, #EC4899 100%); }"
    "</style>"
)
st.markdown(CSS_MODERNO, unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "Você é um especialista em análise de sentimento e extração de dados operacionais do setor de delivery (iFood).\n"
    "Sua tarefa é analisar avaliações de clientes e extrair um objeto JSON estrito com os seguintes aspectos:\n"
    "- comida: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\n"
    "- entrega: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\n"
    "- embalagem: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\n"
    "- custo_beneficio: 'positivo', 'negativo', 'neutro' ou 'nao_mencionado'\n"
    "- risco_churn: true ou false\n"
    "- resumo_critica: frase curta com o problema principal ou null se não houver problemas.\n\n"
    "Responda APENAS com o JSON válido, sem introduções ou explicações."
)

with st.sidebar:
    st.markdown("### ✨ Neural Engine Spec")
    st.caption("Pipeline de triagem ABSA & retenção de clientes treinado via QLoRA (4-bit).")
    st.markdown(
        "<div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px;margin-bottom:16px;font-size:13px;color:#CBD5E1;'>"
        "<div>🔹 <b>Base:</b> Qwen2.5-3B-Instruct</div>"
        "<div style='margin-top:6px;'>🔹 <b>PEFT:</b> LoRA (r=16, α=16)</div>"
        "<div style='margin-top:6px;'>🔹 <b>Contrato:</b> Pydantic v2 Strict</div>"
        "</div>",
        unsafe_allow_html=True
    )
    modelo_ativo = st.selectbox(
        "⚡ Motor de Inferência (API):",
        ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
    )
    st.divider()
    st.markdown("### 📊 Benchmark (Test n=60)")
    metricas_sidebar = [
        ("Aderência JSON Estrito", 100.0),
        ("Entrega & Logística", 100.0),
        ("Detecção de Churn", 98.3),
        ("Embalagem & Lacre", 90.0),
        ("Qualidade da Comida", 85.0),
        ("Custo-Benefício", 81.7)
    ]
    barras_html = ""
    for nome_m, val_m in metricas_sidebar:
        barras_html += (
            f"<div class='metric-row'>"
            f"<div class='metric-head'><span>{nome_m}</span><span style='color:#F43F5E;'>{val_m:.1f}%</span></div>"
            f"<div class='bar-bg'><div class='bar-fill' style='width:{val_m}%;'></div></div>"
            f"</div>"
        )
    st.markdown(barras_html, unsafe_allow_html=True)
    st.divider()
    st.link_button("🤗 Hugging Face • Model Card", "https://huggingface.co/fernandodlts/qwen2.5-3b-delivery-absa-lora", use_container_width=True)
    st.link_button("🗂️ Hugging Face • Dataset (300)", "https://huggingface.co/datasets/fernandodlts/brazilian-delivery-absa-dataset", use_container_width=True)

HERO_SECTION = (
    "<div class='hero-wrapper'>"
    "<div class='status-pill'><span class='live-dot'></span> SISTEMA ONLINE • ABSA & CHURN INTELLIGENCE</div>"
    "<div class='hero-title'>Delivery Review Triage & Extraction Engine</div>"
    "<div class='hero-subtitle'>Cole qualquer avaliação informal de delivery ou selecione um ticket real abaixo. A IA analisa gírias, ironias e múltiplas queixas para classificar cada operação e acionar alertas de retenção em tempo real.</div>"
    "</div>"
)
st.markdown(HERO_SECTION, unsafe_allow_html=True)

if "texto_input" not in st.session_state:
    st.session_state.texto_input = ""

tickets_brutos = {
    "Ticket #4092": "o burger tava surreal de bom quentinho e suculento mas pow atrasou 1h e meia e esqueceram minha coca lata.. pedi estorno no suporte nunca mais peco nessa loja",
    "Ticket #4108": "mano chegou ate rapido e a sacola veio toda lacradinha bonitinha, mas paguei 75 conto num combo q o salmao tava com cheiro estranho e o arroz duro igual pedra.. joguei no lixo p nao passar mal, quero meu reembolso nunca mais compro aqui",
    "Ticket #4155": "o acai é caprichado dms preço super justo pelo tanto de complemento q vem, so que demorou quase 1h pra sair e o copo veio mal fechado vazando leite condensado na sacola toda.. deu trabalho pra limpar mas tava mt bom",
    "Ticket #4201": "melhor frango frito da regiao crocante sequinho tempero brabo dms e chegou fumegando com lacre intacto nota 1000"
}

st.markdown("##### 💬 Simulador de Triagem Cega (Tickets Recebidos)")
st.caption("Clique em um protocolo para carregar a mensagem bruta do cliente ou digite livremente no campo abaixo:")

cols_tickets = st.columns(5)
for idx, (num_ticket, conteudo_bruto) in enumerate(tickets_brutos.items()):
    if cols_tickets[idx].button(f"⚡ {num_ticket}", use_container_width=True):
        st.session_state.texto_input = conteudo_bruto

if cols_tickets[4].button("🧹 Limpar Campo", use_container_width=True):
    st.session_state.texto_input = ""

texto_review = st.text_area(
    "Avaliação do cliente:",
    key="texto_input",
    height=120,
    label_visibility="collapsed",
    placeholder="Ex: o pedido chegou super rápido, mas a embalagem veio rasgada e o lanche totalmente frio..."
)

analisar_btn = st.button("✨ Executar Diagnóstico Neural Autônomo", type="primary", use_container_width=True)

if analisar_btn:
    if not texto_review.strip():
        st.warning("Selecione um Ticket acima ou digite uma avaliação de cliente para iniciar a análise.")
    else:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("Chave GEMINI_API_KEY não encontrada no arquivo .env.")
        else:
            inicio = time.perf_counter()
            with st.spinner("Processando semântica informal e validando contrato Pydantic..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=modelo_ativo,
                        contents=f"{SYSTEM_PROMPT}\n\nAvaliação do cliente:\n{texto_review}",
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AnaliseAspectos,
                            temperature=0.1
                        )
                    )

                    latencia_ms = (time.perf_counter() - inicio) * 1000
                    validado = AnaliseAspectos.model_validate_json(response.text)
                    dados = validado.model_dump()

                    st.write("")
                    if dados["risco_churn"]:
                        banner_html = (
                            f"<div class='banner-churn'>"
                            f"<div>"
                            f"<div style='color:#FB7185;font-weight:800;font-size:17px;letter-spacing:0.3px;margin-bottom:4px;'>"
                            f"🚨 ALERTA DE RETENÇÃO: ALTO RISCO DE CHURN DETECTADO</div>"
                            f"<div style='color:#CBD5E1;font-size:14px;'>"
                            f"Ruptura crítica de experiência identificada. Acionar fluxo imediato de estorno ou cupom de recuperação."
                            f"</div></div>"
                            f"<div class='telemetry-chip'>⚡ {modelo_ativo} • {latencia_ms:.0f} ms</div>"
                            f"</div>"
                        )
                    else:
                        banner_html = (
                            f"<div class='banner-stable'>"
                            f"<div>"
                            f"<div style='color:#34D399;font-weight:800;font-size:17px;letter-spacing:0.3px;margin-bottom:4px;'>"
                            f"✅ CLIENTE ESTÁVEL: SEM RISCO DE ABANDONO (CHURN FALSE)</div>"
                            f"<div style='color:#CBD5E1;font-size:14px;'>"
                            f"Nenhuma intenção de cancelamento definitivo detectada. Comentário registrado na telemetria da loja."
                            f"</div></div>"
                            f"<div class='telemetry-chip'>⚡ {modelo_ativo} • {latencia_ms:.0f} ms</div>"
                            f"</div>"
                        )
                    st.markdown(banner_html, unsafe_allow_html=True)

                    cols = st.columns(4)
                    config_aspectos = [
                        ("🍔", "Comida & Cozinha", "comida"),
                        ("🛵", "Entrega & Prazo", "entrega"),
                        ("📦", "Embalagem & Lacre", "embalagem"),
                        ("💎", "Custo-Benefício", "custo_beneficio")
                    ]
                    nomes_exibicao = {
                        "positivo": "● POSITIVO",
                        "negativo": "● NEGATIVO",
                        "neutro": "● NEUTRO",
                        "nao_mencionado": "○ NÃO CITADO"
                    }

                    for col, (icone, titulo, chave) in zip(cols, config_aspectos):
                        valor = dados[chave]
                        label_texto = nomes_exibicao.get(valor, valor.upper())
                        card_html = (
                            f"<div class='aspect-card card-{valor}'>"
                            f"<div class='icon-circle'>{icone}</div>"
                            f"<div class='aspect-title'>{titulo}</div>"
                            f"<div class='pill-badge pill-{valor}'>{label_texto}</div>"
                            f"</div>"
                        )
                        col.markdown(card_html, unsafe_allow_html=True)

                    col_esq, col_dir = st.columns([1.15, 1])

                    with col_esq:
                        resumo_txt = dados["resumo_critica"] if dados["resumo_critica"] else "Nenhuma falha operacional reportada pelo cliente."
                        cor_resumo = "#FB7185" if dados["resumo_critica"] else "#34D399"

                        acoes = []
                        if dados["comida"] == "negativo":
                            acoes.append("👨‍🍳 <b>Cozinha:</b> Auditar preparo, conservação dos insumos e temperatura de saída.")
                        if dados["entrega"] == "negativo":
                            acoes.append("🛵 <b>Logística:</b> Verificar tempo de despacho da loja e rota do entregador parceiro.")
                        if dados["embalagem"] == "negativo":
                            acoes.append("📦 <b>Packaging:</b> Reforçar vedação de líquidos, lacre de segurança e recipientes internos.")
                        if dados["custo_beneficio"] == "negativo":
                            acoes.append("🏷️ <b>Catálogo:</b> Revisar relação entre peso da porção, descrição e precificação.")

                        acoes_html = ""
                        if acoes:
                            for acao in acoes:
                                acoes_html += f"<div class='action-item'>{acao}</div>"
                        else:
                            acoes_html = "<div class='action-item'>✨ <b>Operação Saudável:</b> Nenhuma intervenção corretiva necessária neste pedido.</div>"

                        painel_esq_html = (
                            f"<div class='glass-panel'>"
                            f"<div style='font-size:16px;font-weight:700;color:#F8FAFC;margin-bottom:12px;'>🎯 Diagnóstico de Causa-Raiz & Playbook</div>"
                            f"<div style='background:rgba(0,0,0,0.28);border-left:4px solid {cor_resumo};padding:12px 16px;border-radius:10px;margin-bottom:16px;'>"
                            f"<div style='font-size:11.5px;text-transform:uppercase;letter-spacing:0.6px;color:#94A3B8;font-weight:700;'>Síntese Extraída pela IA</div>"
                            f"<div style='font-size:14.5px;color:#F1F5F9;font-weight:600;margin-top:4px;'>{resumo_txt}</div>"
                            f"</div>"
                            f"<div style='font-size:12.5px;text-transform:uppercase;letter-spacing:0.6px;color:#94A3B8;font-weight:700;margin-bottom:6px;'>Playbook de Ações Recomendadas</div>"
                            f"{acoes_html}"
                            f"</div>"
                        )
                        st.markdown(painel_esq_html, unsafe_allow_html=True)

                    with col_dir:
                        st.markdown(
                            "<div class='glass-panel' style='padding-bottom:10px;'>"
                            "<div style='font-size:16px;font-weight:700;color:#F8FAFC;margin-bottom:8px;'>🧩 Contrato JSON Validado (Pydantic v2)</div>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        st.json(dados)

                except Exception as e:
                    st.error(f"Falha na inferência: {e}")