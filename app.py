# -*- coding: utf-8 -*-
import json, os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="バイアス監査アプリ",
    layout="wide",                      # ← これが効きます
    initial_sidebar_state="collapsed",  # ← 初期は閉じた状態
)

st.markdown("""
<style>
/* ===== ヒーロー（見出し＋説明＋CTA） ===== */
#cta-hero { padding: 8px 0 6px; }
#cta-hero h2 { margin: 0 0 8px; font-weight: 800; }
#cta-hero p  { margin: 0 14px 12px 0; color: #495057; }

/* ヒーロー下にCTAを密着配置（上の余白ゼロ、下だけ少し） */
#cta-wrap{ margin: 0 0 24px; display:flex; justify-content:center; }

/* Streamlit 1.50対応：CTAボタンを確実に“塗りつぶし”にする */
#cta-wrap .stButton > button,
#cta-wrap button[data-testid="stBaseButton-primary"],
#cta-wrap button[data-testid="baseButton-primary"],
#cta-wrap button[data-testid="stBaseButton-secondary"]{
  background-color: #7AA5A0 !important;  /* ← 好きな色に変えてOK */
  color: #ffffff !important;
  border: none !important;
  border-radius: 14px !important;
  font-weight: 800 !important;
  font-size: 1.05rem !important;
  padding: .85rem 1.2rem !important;
  box-shadow: 0 8px 18px rgba(0,0,0,.16) !important;
  width: min(720px, 100%) !important;
}
#cta-wrap .stButton > button:hover{ filter: brightness(.96) !important; }

/* セクション間の余白（ヒーロー直下を詰め、それ以降は通常） */
.section { margin: 24px 0; }
</style>
""", unsafe_allow_html=True)


# ===== ヒーロー/CTA 専用スタイル（1か所に統一） =====
st.markdown("""
<style>
/* セクションの上下余白・タイポ */
#cta-hero { padding: 12px 0 4px; }
#cta-hero h3 { margin: 0 0 6px; font-weight: 800; }
#cta-hero p  { margin: 0 0 10px; color: #495057; }

/* ボタン配置と見た目（Streamlit 1.50対応） */
#cta-wrap{ margin: 8px 0 24px; display:flex; justify-content:center; }
#cta-wrap .stButton > button,
#cta-wrap button[data-testid="stBaseButton-primary"],
#cta-wrap button[data-testid="baseButton-primary"]{
  background-color:#7AA5A0 !important;   /* 好きな色に変更OK */
  color:#fff !important;
  border:none !important;
  border-radius:14px !important;
  font-weight:800 !important;
  font-size:1.05rem !important;
  padding:.8rem 1.1rem !important;
  box-shadow:0 8px 18px rgba(0,0,0,.16) !important;
  width:min(720px,100%) !important;
}
#cta-wrap .stButton > button:hover{ filter:brightness(.96) !important; }
</style>
""", unsafe_allow_html=True)

# ===== 上部ヒーロー＋CTA =====
st.markdown('<div id="cta-hero">', unsafe_allow_html=True)
st.markdown("## ここからすぐにバイアス分析アプリへ")
st.write("入力は1分。AIがあなたの文章から代表的なバイアスを抽出します。")
st.markdown('<div id="cta-wrap">', unsafe_allow_html=True)
goto_bias_top = st.button("🧠 バイアスを解析する", key="goto_bias_top", use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

if goto_bias_top:
    st.switch_page("pages/1_バイアス分析.py")


import inspect, ui_components

st.markdown("""
<style>
/* サイドバー：開→通常幅、閉→幅ゼロにして隙間を作らない */
section[data-testid="stSidebar"]{ width: 260px; }
section[data-testid="stSidebar"][aria-expanded="false"]{
    width: 0 !important;
    min-width: 0 !important;
}

/* デスクトップ時の本文の最大幅（読みやすさキープ用、お好みで調整） */
@media (min-width: 900px){
  .main .block-container{
    max-width: 960px;   /* 800〜1100pxあたりで調整すると読みやすい */
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

/* モバイルはそのまま全幅でOK */
</style>
""", unsafe_allow_html=True)

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

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 180px !important;     /* デフォルト：約250px */
            min-width: 180px !important; /* 念のため固定 */
        }
        [data-testid="stSidebarNav"] {
            font-size: 1.2rem;           /* タブ文字を少し小さく */
        }
    </style>
""", unsafe_allow_html=True)


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
        submit = st.form_submit_button("🧠 バイアス・プチチェック")


from concurrent.futures import ThreadPoolExecutor, TimeoutError

# --- ボタン処理 ---
if submit:
    if not topic.strip():
        st.warning("内容を入力してください。")
    else:
        st.session_state["ai_result"] = None
        st.session_state["ai_busy"] = True

        try:
            # 解析を実行（AI→ルールベースどちらでもOK）
            ai_result = run_analyze_with_timeout(topic, context_tag)
            st.session_state["ai_result"] = ai_result

        except TimeoutError:
            st.error("サーバーの応答が遅延しています。しばらくして再試行してください。")
        except Exception as e:
            st.error(f"解析中にエラーが発生しました: {e}")
        finally:
            st.session_state["ai_busy"] = False


# --- 結果表示 ---
if "ai_result" in st.session_state and st.session_state["ai_result"]:
    st.markdown("---")
    st.subheader("💭 バイアス・プチチェック結果")
    st.markdown(st.session_state["ai_result"])
else:
    st.info("結果がここに表示されます。")

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
</style>
""", unsafe_allow_html=True)


from pathlib import Path
import streamlit as st

# --- CTAの余白調整（上を0、下だけ広め） ---
st.markdown("""
<style>
#cta-wrap{
  margin: 0 0 48px;                 /* 上0 / 下48px */
  display:flex; justify-content:center;
}
#cta-wrap .stButton > button{
  min-height: 54px;
}
</style>
""", unsafe_allow_html=True)


def _goto_bias_page():
    """
    'pages' フォルダ内から「バイアス分析」を含むページを自動検出して遷移。
    見つからなければエラーメッセージを表示。
    """
    # 1) パスで探す（ファイル名に「バイアス分析」を含む .py）
    candidates = list(Path("pages").glob("*.py"))
    target = None
    for p in candidates:
        if "バイアス分析" in p.stem:  # 例: バイアス分析.py / 1_バイアス分析.py など
            target = p
            break

    if target is not None:
        # 正規パスで遷移
        st.switch_page(str(target.as_posix()))
        return

    # 2) 予備：サイドバー表示名で遷移（例: "バイアス分析" / "1 バイアス分析"）
    try:
        from streamlit_extras.switch_page_button import switch_page
        switch_page("バイアス分析")
    except Exception as e:
        st.error("ページ『バイアス分析』が見つかりません。"
                 "ファイルを `pages/バイアス分析.py`（またはその名前を含む）にしてください。")
        # デバッグ用に一覧を表示（一時的に役立ちます）
        st.caption("検出された pages/:")
        for p in candidates:
            st.caption(f"• {p.name}")
















