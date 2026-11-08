import html

import requests
import streamlit as st

from churn.config import settings

CSS = """
<style>
  :root {
    --surface: #ffffff;
    --ink: #131a2b;
    --muted: #5b6478;
    --line: #e2e7f2;
    --brand: #4f46e5;
    --brand-strong: #4338ca;
    --brand-soft: #eef0ff;
    --risk-high: #e11d48;
    --risk-high-soft: #fdeef1;
    --risk-low: #0f9d8a;
    --risk-low-soft: #e8f8f4;
    --track: #edf0f7;
  }

  .stApp {
    background:
      radial-gradient(circle at 12% -10%, #e8ecff, transparent 46rem),
      radial-gradient(circle at 92% 4%, var(--brand-soft), transparent 34rem),
      #f3f5fb;
    color: var(--ink);
  }

  #MainMenu,
  header[data-testid="stHeader"],
  footer,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"] {
    visibility: hidden;
    height: 0;
  }

  [data-testid="stMainBlockContainer"],
  .block-container {
    max-width: 760px;
    padding-top: 3rem;
    padding-bottom: 3rem;
  }

  .hero {
    text-align: center;
    margin-bottom: 2rem;
  }

  .brand {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 1.3rem;
    color: var(--brand-strong);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }

  .brand-mark {
    display: grid;
    place-items: center;
    width: 2rem;
    height: 2rem;
    border-radius: 0.7rem;
    background: var(--brand);
    box-shadow: 0 10px 20px -10px var(--brand);
    color: #fff;
  }

  .brand-mark svg {
    width: 1.15rem;
    height: 1.15rem;
  }

  .hero h1 {
    margin: 0;
    color: var(--ink);
    font-size: clamp(1.75rem, 4.5vw, 2.6rem);
    line-height: 1.15;
    letter-spacing: -0.025em;
  }

  .hero p {
    max-width: 46ch;
    margin: 0.9rem auto 0;
    color: var(--muted);
    font-size: 1rem;
  }

  .hero code {
    padding: 0.1em 0.4em;
    border-radius: 0.4em;
    background: var(--brand-soft);
    color: var(--brand-strong);
    font-size: 0.9em;
  }

  [data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
  }

  [data-testid="stTextInputRootElement"] {
    height: auto !important;
    min-height: 3.2rem;
    border: 1.5px solid var(--line) !important;
    border-radius: 0.95rem !important;
    background: var(--surface);
    box-shadow: none;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
  }

  [data-testid="stTextInputRootElement"]:focus-within {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 4px var(--brand-soft);
  }

  [data-testid="stTextInputField"] {
    min-height: 3.2rem;
    padding: 0.85rem 1rem;
    background: transparent;
    color: var(--ink);
    font-size: 1rem;
    letter-spacing: 0.02em;
  }

  [data-testid="stTextInputField"]::placeholder {
    color: var(--muted);
    opacity: 0.65;
  }

  [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    padding: clamp(1.5rem, 4vw, 2.4rem) !important;
    border: 1px solid var(--line) !important;
    border-radius: 26px !important;
    background: var(--surface);
    box-shadow: 0 24px 60px -28px rgba(19, 26, 43, 0.28);
  }

  .stButton > button {
    width: 100%;
    min-height: 3.32rem;
    padding: 0.7rem 1.3rem;
    border: none;
    border-radius: 0.95rem;
    background: var(--brand);
    box-shadow: 0 14px 26px -14px var(--brand);
    color: #fff;
    font-size: 0.98rem;
    font-weight: 650;
    transition: background 0.18s ease, transform 0.12s ease;
  }

  .stButton > button:hover {
    background: var(--brand-strong);
    color: #fff;
  }

  .stButton > button:active {
    transform: translateY(1px);
  }

  [data-testid="stButtonGroup"] button[data-variant="pills"] {
    min-height: 0;
    padding: 0.28rem 0.7rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: transparent;
    color: var(--brand-strong);
    font-size: 0.8rem;
    font-weight: 600;
  }

  [data-testid="stButtonGroup"] button[data-variant="pills"]:hover {
    border-color: var(--brand);
    background: var(--brand-soft);
    color: var(--brand-strong);
  }

  [data-testid="stButtonGroup"] button[data-variant="pills"][aria-checked="true"] {
    border-color: var(--brand) !important;
    background: var(--brand-soft) !important;
    color: var(--brand-strong) !important;
  }

  .feedback {
    margin-top: 1.2rem;
    padding: 0.9rem 1.05rem;
    border: 1px solid var(--risk-high);
    border-radius: 0.9rem;
    background: var(--risk-high-soft);
    color: var(--risk-high);
    font-size: 0.92rem;
    font-weight: 550;
  }

  .result {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--line);
    animation: rise 0.35s ease both;
  }

  @keyframes rise {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }

  .result-main {
    display: flex;
    align-items: center;
    gap: clamp(1.2rem, 5vw, 2.4rem);
  }

  .gauge {
    position: relative;
    display: grid;
    flex: 0 0 auto;
    place-items: center;
    width: clamp(9.5rem, 30vw, 11.5rem);
    aspect-ratio: 1;
    border-radius: 50%;
    background: conic-gradient(
      from -90deg,
      var(--risk-color) calc(var(--value) * 1%),
      var(--track) 0
    );
  }

  .gauge::before {
    content: "";
    position: absolute;
    inset: 0.82rem;
    border-radius: 50%;
    background: var(--surface);
  }

  .gauge-inner {
    position: relative;
    padding: 0 0.5rem;
    text-align: center;
  }

  .gauge-inner strong {
    display: block;
    color: var(--ink);
    font-size: clamp(1.7rem, 5vw, 2.15rem);
    font-weight: 750;
    letter-spacing: -0.03em;
    line-height: 1.1;
  }

  .gauge-caption {
    display: block;
    margin-top: 0.15rem;
    color: var(--muted);
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .verdict {
    min-width: 0;
  }

  .badge {
    display: inline-block;
    padding: 0.3rem 0.72rem;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .badge.high {
    background: var(--risk-high-soft);
    color: var(--risk-high);
  }

  .badge.low {
    background: var(--risk-low-soft);
    color: var(--risk-low);
  }

  .verdict h2 {
    margin: 0.6rem 0 0;
    color: var(--ink);
    font-size: clamp(1.15rem, 3vw, 1.45rem);
    line-height: 1.25;
    letter-spacing: -0.015em;
  }

  .verdict p {
    margin: 0.45rem 0 0;
    color: var(--muted);
    font-size: 0.93rem;
  }

  .details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 1.5rem 0 0;
  }

  .details > div {
    padding: 0.8rem 0.95rem;
    border: 1px solid var(--line);
    border-radius: 0.85rem;
    background: #f7f8fd;
  }

  .details dt {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 650;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .details dd {
    margin: 0.25rem 0 0;
    color: var(--ink);
    font-size: 0.95rem;
    font-weight: 600;
    overflow-wrap: anywhere;
  }

  .foot {
    margin-top: 1.6rem;
    color: var(--muted);
    font-size: 0.78rem;
    text-align: center;
  }

  @media (max-width: 560px) {
    [data-testid="stHorizontalBlock"] {
      flex-direction: column;
    }

    [data-testid="stColumn"] {
      width: 100% !important;
      flex: 1 1 100% !important;
    }

    .result-main {
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    .details {
      grid-template-columns: 1fr;
    }
  }
</style>
"""

HERO = """
<div class="hero">
  <div class="brand">
    <span class="brand-mark">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
           stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 16l5-7 4 4 6-9" />
      </svg>
    </span>
    <span>Churn Radar</span>
  </div>
  <h1>Qual a chance deste cliente cancelar?</h1>
  <p>Informe o código do cliente (<code>customerID</code>) e o modelo devolve a
    probabilidade de churn.</p>
</div>
"""


@st.cache_data(ttl=300)
def carregar_exemplos() -> list:
    """Pede à API os customerIDs de exemplo (mesma base usada no treino)."""
    resp = requests.get(f"{settings.api_url}/customers", timeout=10)
    resp.raise_for_status()
    return resp.json()["customer_ids"]


def prever(customer_id):
    """Consulta a probabilidade de churn na API."""
    try:
        resp = requests.get(f"{settings.api_url}/predict/{customer_id}", timeout=10)
    except requests.RequestException:
        return None, "não consegui falar com a API (backend no ar?)"

    if resp.status_code == 404:
        return None, "cliente não encontrado"
    if resp.status_code != 200:
        return None, f"erro na API (HTTP {resp.status_code})"

    return float(resp.json()["churn_probability"]), None


def consultar():
    st.session_state["alvo"] = st.session_state.get("codigo", "").strip()


def usar_exemplo():
    exemplo = st.session_state.get("exemplo")
    if exemplo:
        st.session_state["codigo"] = exemplo
        st.session_state["alvo"] = exemplo


def cartao_resultado(codigo, prob):
    alto = prob >= 0.5
    percentual = f"{prob * 100:.1f}".replace(".", ",")
    cor = "var(--risk-high)" if alto else "var(--risk-low)"
    badge_classe = "high" if alto else "low"
    badge_texto = "Alto risco" if alto else "Baixo risco"
    titulo = "Provável cancelamento" if alto else "Cliente propenso a permanecer"
    texto = (
        "A probabilidade passou do limiar de 50%. Vale priorizar uma ação de retenção."
        if alto
        else "A probabilidade ficou abaixo do limiar de 50%. O cliente tende a continuar ativo."
    )
    previsao = "Vai cancelar (Yes)" if alto else "Permanece (No)"

    st.markdown(
        f"""
        <section class="result">
          <div class="result-main">
            <div class="gauge" style="--value: {prob * 100:.1f}; --risk-color: {cor}">
              <div class="gauge-inner">
                <strong>{percentual}%</strong>
                <span class="gauge-caption">de churn</span>
              </div>
            </div>
            <div class="verdict">
              <span class="badge {badge_classe}">{badge_texto}</span>
              <h2>{titulo}</h2>
              <p>{texto}</p>
            </div>
          </div>
          <dl class="details">
            <div><dt>Cliente</dt><dd>{html.escape(codigo)}</dd></div>
            <div><dt>Previsão</dt><dd>{previsao}</dd></div>
            <div><dt>Limiar de decisão</dt><dd>50%</dd></div>
          </dl>
        </section>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="Churn Radar", page_icon="📉", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)

    try:
        exemplos = carregar_exemplos()
    except requests.RequestException:
        exemplos = []
        st.markdown(
            '<div class="feedback">Sem conexão com a API — suba o backend primeiro '
            "(<code>docker compose up api</code>).</div>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        col_input, col_botao = st.columns([3, 1.15], vertical_alignment="bottom")
        with col_input:
            st.text_input(
                "Código do cliente",
                placeholder="Ex.: SYN-00000",
                key="codigo",
            )
        with col_botao:
            st.button(
                "Consultar",
                type="primary",
                on_click=consultar,
                use_container_width=True,
            )

        st.pills(
            "Experimente",
            exemplos,
            key="exemplo",
            on_change=usar_exemplo,
        )

        alvo = st.session_state.get("alvo")

        if alvo is not None and not alvo:
            st.markdown(
                '<div class="feedback">Digite o código de um cliente para consultar.</div>',
                unsafe_allow_html=True,
            )
        elif alvo:
            prob, erro = prever(alvo)

            if erro:
                st.markdown(
                    f'<div class="feedback">Não foi possível consultar: {html.escape(erro)}.</div>',
                    unsafe_allow_html=True,
                )
            else:
                cartao_resultado(alvo, prob)

    st.markdown(
        '<p class="foot">Probabilidade servida pela Churn API, com o modelo treinado '
        "neste projeto. Uso demonstrativo, não substitui análise de negócio.</p>",
        unsafe_allow_html=True,
    )


main()
