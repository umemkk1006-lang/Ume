import streamlit as st

def hero(title: str, subtitle: str, cta_label: str, cta_anchor: str):
    st.markdown(
        f"""
        <div class="hero">
          <h1>{title}</h1>
          <p class="sub">{subtitle}</p>
          <a href="{cta_anchor}" class="cta">{cta_label}</a>
        </div>
        """, unsafe_allow_html=True
    )
    _inject_css()

def info_cards(items):
    cols = st.columns(len(items))
    for i, it in enumerate(items):
        with cols[i]:
            st.markdown(
                f"""
                <div class="card">
                  <div class="icon">{it.get('icon','')}</div>
                  <div class="title">{it.get('title','')}</div>
                  <div class="desc">{it.get('desc','')}</div>
                </div>
                """, unsafe_allow_html=True
            )

def stepper(steps, active: int = 1):
    parts = []
    for i, s in enumerate(steps, start=1):
        cls = "step active" if i <= active else "step"
        parts.append(f'<div class="{cls}"><span>{i}</span>{s}</div>')
    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)
    _inject_css()

def result_badge(label: str, score: float):
    pct = int(round(score*100))
    st.markdown(
        f"""
        <div class="badge">
          <div class="badge__label">{label}</div>
          <div class="badge__score">{pct}%</div>
        </div>
        """, unsafe_allow_html=True
    )
    _inject_css()

def tip_card(text: str):
    st.markdown(
        f"""
        <div class="tip">
          <span>💡</span>
          <p>{text}</p>
        </div>
        """, unsafe_allow_html=True
    )
    _inject_css()

# ---- minimal CSS（必要なら assets/styles.css に分離） ----
def _inject_css():
    st.markdown("""
    <style>
    :root { --bg:#fafafa; --card:#ffffff; --ink:#222; --muted:#666; --accent:#6c9; }
    .hero { text-align:center; padding:2.5rem 1rem; }
    .hero h1 { margin:0 0 .5rem; font-size:2.0rem; line-height:1.2; }
    .hero .sub { color:var(--muted); margin:.25rem auto 1rem; max-width:42rem; }
    .hero .cta { display:inline-block; padding:.6rem 1rem; border-radius:.6rem; background:var(--accent); color:#003; text-decoration:none; font-weight:600; }
    .card { background:var(--card); border:1px solid #eee; border-radius:.8rem; padding:1rem; text-align:center; margin:.5rem 0; }
    .card .icon { font-size:1.4rem; }
    .card .title { font-weight:700; margin:.4rem 0 .2rem; }
    .card .desc { color:var(--muted); font-size:.95rem; line-height:1.5; }
    .stepper { display:flex; gap:.5rem; align-items:center; margin:1rem 0 1.5rem; flex-wrap:wrap;}
    .stepper .step { display:flex; align-items:center; gap:.4rem; color:#999; font-size:.9rem; }
    .stepper .step span { width:1.3rem; height:1.3rem; border-radius:50%; background:#ddd; color:#333; display:inline-flex; align-items:center; justify-content:center; font-size:.8rem;}
    .stepper .active { color:#111; }
    .stepper .active span { background:var(--accent); color:#003; }
    .badge { background:var(--card); border:1px solid #eee; border-radius:.8rem; padding:.8rem; text-align:center; margin:.25rem 0; }
    .badge__label { font-weight:600; margin-bottom:.2rem; }
    .badge__score { font-size:1.2rem; font-weight:800; }
    .tip { display:flex; gap:.6rem; align-items:flex-start; background:#f4fff9; border:1px solid #def7ea; padding:.8rem; border-radius:.6rem; margin:.4rem 0; }
    </style>
    """, unsafe_allow_html=True)

import streamlit as st

def stepper(steps, active: int = 1):
    parts = []
    for i, s in enumerate(steps, start=1):
        cls = "step active" if i <= active else "step"
        parts.append(f'<div class="{cls}"><span>{i}</span>{s}</div>')
    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)
    _inject_css()

def result_badge(label: str, score: float):
    pct = int(round(score * 100))
    st.markdown(
        f"""
        <div class="badge">
          <div class="badge__label">{label}</div>
          <div class="badge__score">{pct}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _inject_css()

def tip_card(text: str):
    st.markdown(
        f"""
        <div class="tip">
          <span>💡</span>
          <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _inject_css()

def _inject_css():
    st.markdown("""
    <style>
    :root { --bg:#fafafa; --card:#ffffff; --ink:#222; --muted:#666; --accent:#6c9; }
    .hero { text-align:center; padding:2.5rem 1rem; }
    .hero h1 { margin:0 0 .5rem; font-size:2.0rem; line-height:1.2; }
    .hero .sub { color:var(--muted); margin:.25rem auto 1rem; max-width:42rem; }
    .hero a.cta { display:inline-block; padding:.6rem 1rem; border-radius:.6rem; background:var(--accent); color:#003; text-decoration:none; font-weight:600; }

    .card { background:var(--card); border:1px solid #eee; border-radius:.8rem; padding:1rem; text-align:center; margin:.5rem 0; }
    .card .icon { font-size:1.4rem; }
    .card .title { font-weight:700; margin:.4rem 0 .2rem; }
    .card .desc { color:var(--muted); font-size:.95rem; line-height:1.5; }

    .stepper { display:flex; gap:.5rem; align-items:center; margin:1rem 0 1.5rem; flex-wrap:wrap;}
    .stepper .step { display:flex; align-items:center; gap:.4rem; color:#999; font-size:.9rem; }
    .stepper .step span { width:1.3rem; height:1.3rem; border-radius:50%; background:#ddd; color:#333; display:inline-flex; align-items:center; justify-content:center; font-size:.8rem;}
    .stepper .active { color:#111; }
    .stepper .active span { background:var(--accent); color:#003; }

    .badge { background:var(--card); border:1px solid #eee; border-radius:.8rem; padding:.8rem; text-align:center; margin:.25rem 0; }
    .badge__label { font-weight:600; margin-bottom:.2rem; }
    .badge__score { font-size:1.2rem; font-weight:800; }

    .tip { display:flex; gap:.6rem; align-items:flex-start; background:#f4fff9; border:1px solid #def7ea; padding:.8rem; border-radius:.6rem; margin:.4rem 0; }
    </style>
    """, unsafe_allow_html=True)
