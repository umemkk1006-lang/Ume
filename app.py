# -*- coding: utf-8 -*-
import json, os
from datetime import datetime
import pandas as pd
import streamlit as st

import inspect, ui_components
st.caption(f"HERO SIG: {inspect.signature(ui_components.hero)}")

# --- AIクライアント & 簡易解析 ---
from openai import OpenAI

def _get_openai_client():
    # Streamlit Secrets → 環境変数の順で見る
    key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        return OpenAI(api_key=key)
    except Exception:
        return None

_openai_client = _get_openai_client()

# この行（25行目）から下の旧 analyze_with_ai を削除し、
# ↓ 以下を貼り付けてください

def analyze_with_ai(text: str):
    """入力テキストを LLM に渡して JSON で返す（簡易解析）"""
    if not _openai_client or not text.strip():
        return None

    system = (
        "あなたは行動経済学と認知心理学に詳しいアナリストです。"
        "ダニエル・カーネマンのシステム1/2にも言及しつつ、"
        "可能性のあるバイアスを特定し、JSONで返して下さい。"
        '返却形式: {"summary":"...", "biases":[{"name":"...", "score":0-1, "reason":"..."}], "tips":["...","..."]}'
    )
    user = f"対象テキスト:\n<<< {text} >>>"

    # フォールバック順
    models = ["gpt-4o-mini", "gpt-4o-mini-2024-07-18", "gpt-4o"]

    import time, json
    last_err = None
    for model in models:
        # 3回まで指数バックオフ
        for attempt in range(3):
            try:
                resp = _openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role":"system","content":system},
                              {"role":"user","content":user}],
                    response_format={"type":"json_object"},
                    temperature=0.2,
                    max_tokens=600,
                    timeout=30,
                )
                return json.loads(resp.choices[0].message.content)
            except Exception as e:
                last_err = e
                time.sleep(1.5 * (2 ** attempt))  # 再試行
                continue
        continue

    st.warning(f"AI解析エラー：{type(last_err).__name__}")
    return None

from ui_components import hero, info_cards, stepper
# 既存ロジックは2ページ目で使う想定。ここは導入と入力のみ。

st.set_page_config(page_title="Bias Audit Lab", page_icon="🧠", layout="centered")

# --- セッション初期化 ---
for k, v in {
    "user_input": "",
    "context_tag": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# hero は見出しだけにして、CTAは付けない
hero(
    title="あなたの“思い込み”、AIで見抜ける？",
    subtitle="心理学×行動経済学のレンズで振り返るミニツール",
    variant="ghost",
)

stepper(steps=["導入", "入力", "解析"], active=2)

st.markdown("### 心理学の視点：私たちの判断は“クセ”を持つ")
st.write(
"""
心理学では、判断や意思決定には無意識の“クセ（バイアス）”が入りやすいことが知られています。
ノーベル経済学賞を受賞した**ダニエル・カーネマン**（『ファスト＆スロー』）は、私たちの思考を大きく2つのモードに分けました。
"""
)

st.markdown("#### システム1（直感の思考）")
st.write(
"""
- 速い・自動・省エネ。パターン認識や連想に強い  
- ただし**思い込みの影響を受けやすい**（例：雰囲気で判断、印象に引っぱられる）
"""
)

st.markdown("#### システム2（熟考の思考）")
st.write(
"""
- ゆっくり・注意深い・論理的。複雑な計算や比較に強い  
- ただし**面倒でサボりがち**。疲れていると動かない
"""
)

st.markdown("### 行動経済学：人は“合理的”とは限らない")
st.write(
"""
行動経済学は、現実の人間行動を心理学的にとらえて“合理的ではない選択”が起きる理由を説明します。代表的な理論と現象は次のとおり：
"""
)
st.markdown("- **プロスペクト理論（カーネマン＆トヴェルスキー）**")
st.write("利益よりも損失の痛みを大きく感じる（**損失回避**）。同じ±1でも、損の方が約2倍重く感じます。")

st.markdown("- **アンカリング**")
st.write("最初に見た数字や情報が“アンカー（いかり）”となり、後の判断を引っぱる。")

st.markdown("- **確証バイアス**")
st.write("自分の信じたい情報ばかり集め、反証を無視する傾向。")

st.markdown("- **利用可能性ヒューリスティック**")
st.write("思い出しやすい（印象に残る）出来事を、実際よりも起こりやすいと見積もる。")

st.markdown("- **フレーミング効果**")
st.write("同じ内容でも“言い回し（フレーム）”次第で選好が変わる（例：生存率90% vs. 死亡率10%）。")

st.caption("→ このアプリは、あなたの入力にこれらの“クセ”がどの程度表れているかを可視化し、対処ヒントを提案します。")


st.markdown("### 日常はバイアスだらけ")
st.caption("ニュースの読み方、買い物、投資、進路や仕事の判断…“無意識のクセ”が入ります。だからこそ、いったん点検してみよう。")

st.markdown("<div id='bias_input'></div>", unsafe_allow_html=True)
st.markdown("## あなたの気になる話題、バイアスがかかってないか見てみる")



with st.form("bias_input_form", clear_on_submit=False):
    topic = st.text_area(
        "例：『このニュースは信じて良い？』『◯◯の株を買うべき？』『この口コミは当てになる？』",
        height=120,
        placeholder="自由に入力してください。要点だけでもOK。"
    )
    col1, col2 = st.columns([1,1])
    with col1:
        context_tag = st.selectbox(
            "カテゴリ（任意）", ["未選択", "ニュース", "投資・お金", "キャリア・進路", "健康", "その他"]
        )
    with col2:
        submit = st.form_submit_button("AIで解析する")


# --- 解析処理と結果表示 ---
if submit:  # 「AIで解析する」ボタンが押されたとき
    if not topic.strip():
        st.warning("内容を入力してください。")
    else:
        with st.spinner("AIが解析中です..."):
            ai_result = analyze_with_ai(topic)  # ← ここでAI解析関数を呼び出す

        # 結果をセッションに保存
        st.session_state["ai_result"] = ai_result

# --- 結果表示 ---
if "ai_result" in st.session_state:
    st.markdown("---")
    st.subheader("AI解析結果")
    st.markdown(st.session_state["ai_result"])
    

# ---- ここからが新規：結果カードを常時表示 ----
st.markdown('<div class="ai-result">', unsafe_allow_html=True)

ai_quick = st.session_state.get("ai_quick")
if ai_quick:
    # 解析結果あり → カードに表示
    st.markdown(f'<div class="card"><pre>{ai_quick}</pre></div>', unsafe_allow_html=True)
else:
    # 未実行/空 → プレースホルダーを表示（スペース確保）
    st.markdown('<div class="card muted">AIの解析結果がここに表示されます。</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# === モバイル最適化CSS ===
st.markdown("""
<style>
/* 全体レイアウト */
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 2rem;
    max-width: 720px;
    margin: auto;
}

/* タイトル・サブタイトル */
h1 {
    font-size: 1.5rem !important;
    text-align: center;
    margin-bottom: 0.3em;
}
.subtitle {
    text-align: center;
    font-size: 0.9rem;
    color: #6c757d;
    margin-bottom: 1em;
}

/* 流れ部分（①〜⑤） */
.process {
    text-align: center;
    font-size: 0.85rem;
    background-color: #f9fafb;
    border-radius: 8px;
    padding: 0.3em 0.6em;
    margin-bottom: 1.2em;
}

/* セクション見出し */
h2, h3, .stSubheader {
    font-size: 1.15rem !important;
    margin-top: 1.6em !important;
    margin-bottom: 0.8em !important;
}

/* 説明文・本文 */
p, .stMarkdown {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #333;
}

/* 入力フォーム調整 */
.stTextInput, .stNumberInput, .stMultiSelect {
    font-size: 0.9rem;
}
.stButton button {
    font-size: 0.9rem;
    padding: 0.5em 1.2em;
    border-radius: 6px;
}

/* Expander調整 */
.streamlit-expanderHeader {
    font-size: 0.9rem !important;
    color: #444 !important;
}

/* 成功/注意メッセージのデザイン */
.stSuccess, .stInfo, .stWarning {
    font-size: 0.9rem;
}

/* 小さい画面時のフォント縮小 */
@media (max-width: 480px) {
    h1 { font-size: 1.3rem !important; }
    h2, h3, .stSubheader { font-size: 1.05rem !important; }
    p, .stMarkdown { font-size: 0.9rem; }
}
</style>
""", unsafe_allow_html=True)

# ---- Page-wide styles ----
st.markdown("""
<style>
/* 中央寄せ＋幅の制御 */
.center-btn { display:flex; justify-content:center; }
.center-btn .stButton { width: 100%; max-width: 360px; }

/* 大きめ・薄色のボタン（このブロック内のボタンだけ効く） */
.center-btn button {
  padding: 1.0rem 1.2rem;
  font-size: 1.05rem;
  border-radius: 10px;
  background: #eaf6f3;         /* 薄いミント */
  color: #0f766e;               /* 濃いグリーン */
  border: 1px solid #cfe7e2;
}

/* AI結果カード（常に枠を見せる） */
.ai-result .card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: .9rem 1rem;
  background: #ffffff;
  min-height: 120px;            /* スペースを確保 */
}
.ai-result .card.muted{
  background:#fafafa;
  color:#6b7280;
}
.ai-result pre{
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;

st.markdown("""
<style>
/* Streamlit 1.50以降対応ボタンスタイル */
.st-emotion-cache-7ym5gk button,
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-secondary"],
div.stButton > button {
    background-color: #7AA5A0 !important;  /* ← ボタンの色 */
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    font-size: 1.1rem !important;
    padding: 0.8em 1.3em !important;
    box-shadow: 0 6px 14px rgba(0,0,0,0.15) !important;
}
.st-emotion-cache-7ym5gk button:hover,
button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(0.95) !important;
}
</style>
""", unsafe_allow_html=True)


goto_bias = st.button("🧠 バイアスを解析する", key="goto_bias", use_container_width=True)


