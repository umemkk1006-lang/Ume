
import streamlit as st
import random
def confidence_letter(score: float):
    """0.0〜1.0をA/B/Cの確からしさに変換"""
    if score >= 0.8: return "A", "高い（かなり当てはまりそう）"
    if score >= 0.6: return "B", "中くらい（それっぽいが他の可能性も）"
    return "C", "低め（参考程度）"

import streamlit as st  # ←先頭に入っていることを確認

def render_finding_card(f: dict):
    # 安全な取り出し（型も整える）
    label = str(f.get("label", "（名称未設定）"))
    score = float(f.get("score", 0.0) or 0.0)
    tips  = list(f.get("suggestions") or [])
    evid  = list(f.get("evidence") or [])
    why   = str(f.get("why", ""))

    st.markdown(f'<div class="card"><b>{label}</b>'
                f'<span class="badge">確からしさ: {score:.2f}</span></div>',
                unsafe_allow_html=True)

    if why:
        st.markdown(f"**なぜ？（短い説明）**　{why}")

    if evid:
        st.caption("ヒントになった言葉: " + "、".join(map(str, evid[:3])))

    if tips:
        st.markdown("**すぐ試せる対処**")
        for t in tips[:4]:
            st.markdown("- " + str(t))


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

# ================================
# 🔧 仮のAI解析関数（後で本処理に置き換えOK）
# ================================
def analyze_with_ai(text, category=None):
    """
    テキストをAIで解析するダミー関数（動作確認用）
    """
    # ここではAIを使わずダミーの結果を返す
    result = f"""
    🧠 入力内容: {text}
    📂 カテゴリ: {category or "未選択"}
    ---
    ✅ 解析結果サンプル：
    「確証バイアス」が含まれる可能性があります。
    （自分の信じたい情報を優先して受け取る傾向）
    """
    return result


