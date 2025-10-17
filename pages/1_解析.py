# -*- coding: utf-8 -*-
# pages/2_バイアス解析.py

import streamlit as st
from logic_simple import analyze_selection   
# =========================
# ページ固有のキー（衝突防止）
# =========================
KEY_PREFIX = "p2_"
def k(name: str) -> str:
    return KEY_PREFIX + name

# =========================
# モバイル最適CSS（読みやすい文字）
# =========================
st.markdown("""
<style>
.block-container{max-width:720px;margin:auto;}
h1{font-size:1.6rem !important;margin:1.8rem 0 1rem 0;}   /* ←タイトルを少し大きく */
h2, .stSubheader{font-size:1.1rem !important;}            /* ←サブ見出しを少し小さく */
p, .stMarkdown{font-size:.95rem;line-height:1.6;}         
.small{color:#667085;font-size:.88rem;}
.stButton>button{font-size:.95rem;padding:.35rem 1rem;}
@media(max-width:480px){
    h1{font-size:1.4rem !important;}   /* モバイルでは少し抑える */
    h2, .stSubheader{font-size:1.0rem !important;}
    p, .stMarkdown{font-size:.92rem;}
}
</style>
""", unsafe_allow_html=True)


# =========================
# ヘッダー
# =========================
st.markdown("# 🧠 バイアス解析（かんたん版）")
st.caption("「“思考のバグ”を見つけて、脳の使い方をアップデート")

# =========================
# 3段階 かんたん入力
# =========================
st.subheader("1) かんたん入力（3ステップ）")

# STEP1: テーマ（シーン）
THEMES = ["お金", "学び", "人間関係", "買い物", "仕事・バイト"]
theme = st.radio("A. どのテーマ？", THEMES, key=k("theme"))

# STEP2: 状況（目的）
SITUATIONS = {
    "お金": ["貯金したい", "出費を減らしたい", "投資が気になる"],
    "学び": ["勉強が続かない", "資格を取りたい", "部活・勉強の両立"],
    "人間関係": ["LINEの既読が気になる", "断れなくて困る", "友だちに意見が言えない"],
    "買い物": ["高い物を買うか迷う", "セールで衝動買い", "サブスクの継続"],
    "仕事・バイト": ["シフトを増やすか迷う", "新しいことに挑戦", "上手く頼れない"],
}
situation = st.selectbox("B. 具体的な状況は？", SITUATIONS[theme], key=k("situation"))

# STEP3: 心のサイン
SIGNS = ["時間がない気がする", "損するのが怖い", "みんながやってるから", "なんとなく不安", "面倒で先のばし"]
sign = st.selectbox("C. 今の気持ちに近いものは？", SIGNS, key=k("sign"))

st.markdown('<span class="small">ヒント：A→B→Cを選ぶと“今の自分の思考のクセ”が浮きやすくなります。</span>', unsafe_allow_html=True)

# 文章（任意。なくてもOK）
st.subheader("2) 一言メモ（任意）")
user_text = st.text_area("今の気持ちや状況を1〜3行で。空でもOK。", key=k("memo"), placeholder="例）セールで安いと聞くと買わなきゃ損な気がして焦る。")

# ==========
# 解析ボタン（ここ1箇所だけ）
# ==========
if st.button("解析する", type="primary", key=k("analyze_btn")):
    # --- ここで簡単解析ロジックを呼ぶ ---
    findings = analyze_selection(theme, situation, sign, user_text)
    # 結果をセッションに保存（None防止）
    st.session_state[k("findings")] = findings or []
    st.session_state[k("debug")] = dbg

    st.success("解析しました。下の結果をご確認ください。")

# =========================
# 解析結果の表示
# =========================
st.subheader("3) 解析結果")
findings = st.session_state.get(k("findings"), None)

if findings is None:
    st.caption("（まだ解析していません）")
elif len(findings) == 0:
    st.success("今回は偏りは見つかりませんでした。落ち着いて考えられています。")
    st.info("友だちに“どう考えたか”を説明してみると、さらに判断が強くなります。")
else:
    st.caption("※ “確からしさ”はA/B/Cの3段階（A:高い｜B:中くらい｜C:低め）")
    for f in findings:
        render_finding_card(f)

# =========================
# 友だちに話したくなる小ネタ
# =========================
with st.expander("おまけ：今日の豆知識"):
    st.markdown("- **フレーミング効果**：同じ内容でも「90%成功」と言われると良く見え、「10%失敗」と言われると悪く見える。")
    st.markdown("- **アンカリング**：最初に見た数字（定価など）が頭に残り、後の判断に影響する。")
    st.markdown("- **現状維持バイアス**：今のままを選びやすい。変えるのが悪いわけじゃない。準備が大事。")

# =========================
# ---------- ロジック ----------
# =========================

def confidence_letter(score: float):
    """0.0〜1.0をA/B/Cの確からしさに変換"""
    if score >= 0.8: return "A", "高い（かなり当てはまりそう）"
    if score >= 0.6: return "B", "中くらい（それっぽいが他の可能性も）"
    return "C", "低め（参考程度）"

def render_finding_card(f: dict):
    """1件分のカード表示（やさしい説明つき）"""
    label = f.get("label", "（名称未設定）")
    score = float(f.get("score", 0.0) or 0.0)
    letter, expl = confidence_letter(score)
    tips = f.get("suggestions", [])
    evid = f.get("evidence", [])
    why = f.get("why", "")

    st.markdown(f'<div class="card"><b>{label}</b><span class="badge">確からしさ: {letter}</span><br><span class="small">{expl}</span></div>', unsafe_allow_html=True)
    if why:
        st.markdown(f"**なぜ？（短い説明）**  {why}")
    if evid:
        st.caption("ヒントになった言葉：" + "、".join(evid[:3]))
    if tips:
        st.markdown("**すぐ試せる対処**")
        for t in tips[:4]:
            st.markdown("- " + t)

def analyze_selection(theme: str, situation: str, sign: str, text: str):
    """
    かんたんルールベース：
      - A/B/C各ステップの組み合わせと、テキスト内のキーワードから
        代表的なバイアス候補を返す
    """
    text = (text or "").lower()

    # 候補辞書：分かりやすい日本語ラベル＋やさしい説明＋行動ヒント
    BIASES = [
        {
            "key": "loss_aversion",
            "label": "損失回避（損を強く避けたくなる）",
            "why": "人は同じ量の得より、同じ量の損を2倍くらい強く感じがちです。",
            "match": lambda th, si, sg, tx: ("損" in sg) or ("損" in tx) or (th=="買い物" and "セール" in tx),
            "tips": [
                "損ではなく“合計いくら払うか”で見る（%ではなく円・時間に言い換える）",
                "買わない選択も候補に入れて3つの案を比べる",
                "一晩おいてからもう一度判断する（24時間ルール）"
            ],
            "score": lambda th, si, sg, tx: 0.8 if ("損" in sg or "セール" in tx) else 0.65
        },
        {
            "key": "anchoring",
            "label": "アンカリング（最初の数字に引っぱられる）",
            "why": "最初に見た定価や点数が“基準”になって、その後の判断がゆがみます。",
            "match": lambda th, si, sg, tx: ("定価" in tx) or ("元値" in tx) or ("セール" in tx),
            "tips": [
                "比べる数字を2つ以上にする（相場・ベースレートを見る）",
                "“今の自分に必要か”で判断する（数字だけで決めない）"
            ],
            "score": lambda th, si, sg, tx: 0.7 if ("定価" in tx or "元値" in tx) else 0.6
        },
        {
            "key": "framing",
            "label": "フレーミング効果（言い方で印象が変わる）",
            "why": "『90%成功』と『10%失敗』は中身が同じでも感じ方が変わります。",
            "match": lambda th, si, sg, tx: ("成功" in tx and "失敗" in tx) or (th in ["買い物","お金"] and "割引" in tx),
            "tips": [
                "別の言い方に言い換えてから判断（%⇔円、得⇔損）",
                "第三者の短評を3行で書く（外部視点）"
            ],
            "score": lambda th, si, sg, tx: 0.6
        },
        {
            "key": "status_quo",
            "label": "現状維持バイアス（変えない方を選びやすい）",
            "why": "人は慣れた状態を好みます。変えるのが悪いわけではなく準備が必要なだけ。",
            "match": lambda th, si, sg, tx: ("面倒" in sg) or ("いつも通り" in tx) or ("先のばし" in sg),
            "tips": [
                "“やるなら最初の1歩だけ”を決める（5分だけ・1問だけ）",
                "やらないコスト（時間・お金・機会）を書き出す"
            ],
            "score": lambda th, si, sg, tx: 0.65 if ("面倒" in sg or "先のばし" in sg) else 0.55
        },
        {
            "key": "bandwagon",
            "label": "同調バイアス（みんなに合わせすぎる）",
            "why": "『みんなやってる』は安心するけど、自分に合うかは別問題です。",
            "match": lambda th, si, sg, tx: ("みんな" in sg) or ("流行" in tx),
            "tips": [
                "利点と不安を1行ずつ書き出し“自分の目的”に合うか確認",
                "合わない所だけ別の方法を探す（全部マネしなくてOK）"
            ],
            "score": lambda th, si, sg, tx: 0.6
        },
        {
            "key": "affect",
            "label": "感情ヒューリスティック（不安や焦りで判断しがち）",
            "why": "強い感情は『今すぐ決めたい！』を生み、損得の見え方を変えます。",
            "match": lambda th, si, sg, tx: ("不安" in sg) or ("焦" in tx) or ("怖" in tx),
            "tips": [
                "深呼吸→10分後の自分が何と言うかを書いてみる（外部視点）",
                "いま決めない（24時間ルール）"
            ],
            "score": lambda th, si, sg, tx: 0.7 if ("焦" in tx or "怖" in tx) else 0.6
        },
    ]

    hits = []
    for spec in BIASES:
        if spec["match"](theme, situation, sign, text):
            hits.append({
                "label": spec["label"],
                "why": spec["why"],
                "evidence": [theme, situation, sign] + ([w for w in ["セール","定価","元値","成功","失敗","焦","怖","不安"] if w in text])[:3],
                "suggestions": spec["tips"],
                "score": spec["score"](theme, situation, sign, text),
            })

    # 重複や似たものを上限3件に
    hits = sorted(hits, key=lambda x: x["score"], reverse=True)[:3]
    return hits
