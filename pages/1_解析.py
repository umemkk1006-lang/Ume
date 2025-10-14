# -*- coding: utf-8 -*-
# pages/1_解析.py

import os, json
import streamlit as st

# ========= 解析ロジック（UIより上に置く） =========

SOFT_CUES = {
    "confirmation": ["確信", "間違いない", "絶対", "都合の良い", "見たいものだけ"],
    "sunk_cost": ["せっかく", "ここまでやった", "元を取る", "もったいない"],
    "loss_aversion": ["損したくない", "無駄", "後悔"],
    "availability": ["よく聞く", "みんな言ってる", "SNSで見た", "バズってる"],
    "framing": ["お得", "限定", "今だけ", "先着"],
}
EMOTION_WORDS = ["不安", "焦り", "ワクワク", "怖い", "嬉しい", "悔しい", "怒り", "緊張"]

def load_rules() -> dict:
    default_rules = {
        "confirmation": {
            "label": "確証バイアス",
            "explain": "自分の考えに合う情報ばかりを集め、反対の意見を無視してしまう思考のくせ。",
            "keywords": ["自分の考えに合う", "都合が良い", "反対の情報を無視"],
            "interventions": [
                "反対の証拠を最低1つ探してみよう",
                "立場が逆の人になりきって主張を書いてみよう",
            ],
        },
        "sunk_cost": {
            "label": "サンクコストの誤謬",
            "explain": "これまで使った時間やお金がもったいなくて、続けるか迷う心理。",
            "keywords": ["ここまで投資", "もったいない", "元を取る"],
            "interventions": [
                "今から始めるとしても同じ判断をするか？を考えてみよう",
                "未来の利益だけで判断してみよう",
            ],
        },
        "loss_aversion": {
            "label": "損失回避バイアス",
            "explain": "得よりも『損したくない』気持ちが強くなる心理。",
            "keywords": ["損したくない", "失う", "無駄になる"],
            "interventions": [
                "失うものと得られるものを並べて比べよう",
                "目的（何のため？）を思い出して判断しよう",
            ],
        },
        "availability": {
            "label": "利用可能性ヒューリスティック",
            "explain": "よく聞く/最近見た情報ほど『正しい』と感じてしまう思い込み。",
            "keywords": ["よく聞く", "SNSで見た", "話題"],
            "interventions": [
                "SNSではなく一次情報（公式サイトなど）を1つ確認しよう",
                "話題性と現実の確率を分けて考えよう",
            ],
        },
        "framing": {
            "label": "フレーミング効果",
            "explain": "『お得！』『今だけ！』などの言い方で判断が変わる心理。",
            "keywords": ["お得", "割引", "限定", "今だけ", "先着"],
            "interventions": [
                "別表現（損/得）に言い換えて比べてみよう",
                "長期的なコストやリスクを見直そう",
            ],
        },
    }
    try:
        with open(os.path.join(os.getcwd(), "rules.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_rules

RULES = load_rules()

def analyze_text(text: str, rules: dict, sensitivity: int):
    text = (text or "").strip()
    if not text:
        return [], {}
    threshold = 1.20 - (sensitivity / 100) * 0.80
    findings, debug_scores = [], {}

    for key, spec in rules.items():
        score, evidences = 0.0, []
        for kw in spec.get("keywords", []):
            if kw and kw in text:
                score += 1.0; evidences.append(kw)
        for soft_kw in SOFT_CUES.get(key, []):
            if soft_kw and soft_kw in text:
                score += 0.5; evidences.append(soft_kw)

        if score >= threshold:
            conf = "A" if score >= (threshold + 0.8) else "B"
            findings.append({
                "type": key, "label": spec.get("label", key),
                "explain": spec.get("explain", ""),
                "confidence": conf, "evidence": evidences,
                "suggestions": spec.get("interventions", []),
                "score": round(score, 2),
            })
        debug_scores[spec.get("label", key)] = round(score, 2)

    emo_hits = [w for w in EMOTION_WORDS if w in text]
    emo_score = 0.5 * len(emo_hits)
    if emo_score >= max(0.5, threshold * 0.6):
        findings.append({
            "type": "affect",
            "label": "感情ヒューリスティック",
            "explain": "不安・焦り・嬉しさなどの感情が判断を左右してしまう心理。",
            "confidence": "B" if emo_score < (threshold + 0.8) else "A",
            "evidence": emo_hits,
            "suggestions": ["一晩おいて再評価（24時間ルール）", "第三者の短評（外部視点）を3行もらう"],
            "score": round(emo_score, 2),
        })
    debug_scores["感情ヒューリスティック"] = round(emo_score, 2)

    findings.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return findings, {"threshold": round(threshold, 2), "scores": debug_scores}

# ========= UI =========

st.set_page_config(page_title="バイアス解析アプリ", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
h1 {text-align:center;font-size:1.5rem;margin-bottom:.2rem;}
h2, h3 {font-size:1.05rem;margin:.9rem 0 .35rem;}
.small {color:#666;font-size:.9rem;text-align:center;margin-bottom:.5rem;}
.result-card {border:1px solid #eaeaea;border-radius:10px;padding:.8rem;margin-bottom:.6rem;background:#fdfdff;}
.badge {display:inline-block;padding:.1rem .4rem;border-radius:999px;background:#eef;margin-left:.3rem;font-size:.8rem;}
.explain {font-size:.9rem;color:#444;margin-bottom:.4rem;}
.tip {font-size:.95rem}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧠 バイアス解析アプリ</h1>", unsafe_allow_html=True)
st.markdown('<div class="small">Self-Bias Monitor（スマホ対応／高校生でも使いやすい）</div>', unsafe_allow_html=True)

# ---------- 1) 設定 ----------
with st.expander("設定（任意）", expanded=False):
    st.session_state["sensitivity"] = st.slider("検出の敏感さ（高いほど拾いやすい）", 0, 100, st.session_state.get("sensitivity", 50))

# ---------- 2) 簡単入力（選択式） ----------
st.markdown("### 1. かんたん入力（選択式）")

THEMES = ["家計・お金", "仕事・キャリア", "学び・自己成長", "人間関係", "ライフスタイル"]
SITUATIONS = ["買うか迷う", "やめるか続ける", "選ぶ・比べる", "頼む/断る", "参加するか迷う"]
EXAMPLES = {
    "買うか迷う": ["PCを買う", "スマホ買い替え", "大型家電を買う", "旅行を予約する"],
    "やめるか続ける": ["部活を続けるか", "塾をやめるか", "SNSを休むか"],
    "選ぶ・比べる": ["A社とB社どっち", "文系/理系どっち", "ノートPCの機種選び"],
    "頼む/断る": ["友だちの依頼を断る？", "親に相談する？", "先生に延長を頼む？"],
    "参加するか迷う": ["サークルに入る？", "ボランティアに行く？", "アルバイトを始める？"],
}

colA, colB = st.columns(2)
with colA:
    theme = st.radio("テーマを選ぶ", THEMES, horizontal=False, key="q_theme")
with colB:
    situation = st.selectbox("状況を選ぶ", SITUATIONS, key="q_sit")

example = st.selectbox("具体例を選ぶ", EXAMPLES.get(situation, []), key="q_example")

choices_default = "今すぐ決める, 少し待つ, 今回は見送る"
choices = st.text_input("選択肢（カンマ区切りで編集可）", value=choices_default, key="q_choices")

# 自動プレビュー（編集可）
def make_preview(theme, situation, example, choices):
    c = [s.strip() for s in (choices or "").split(",") if s.strip()]
    c_txt = "、".join(c[:3])
    return (
        f"{example} を検討しています（テーマ：{theme} / 状況：{situation}）。"
        "良い条件に感じる一方で、後で後悔しないか不安もあります。"
        "代替案や判断材料を揃えてから決めたいです。"
        f" 今回の選択肢は「{c_txt}」です。"
    )

preview = make_preview(theme, situation, example, choices)
st.text_area("自動生成プレビュー（編集可）", preview, key="preview_box", height=140)

if st.button("この内容を下の入力欄へ反映", use_container_width=True):
    st.session_state["main_text"] = st.session_state["preview_box"]
    st.success("下の入力欄に反映しました👇")

st.divider()

# ---------- 3) 今日の意思決定（自由入力） ----------
st.markdown("### 2. 今日の意思決定（入力）")
text = st.text_area(
    "今日、あなたが迷っていることや決めたいことを書いてください。",
    value=st.session_state.get("main_text", ""),
    height=180,
    key="free_text",
)

# ---------- 4) 解析 ----------
if st.button("バイアスを解析する", type="primary", use_container_width=True):
    if not (text or "").strip():
        st.warning("入力が空です。内容を記入してください。")
    else:
        with st.spinner("考え方をチェック中..."):
            findings, debug = analyze_text(text, RULES, st.session_state.get("sensitivity", 50))
        st.session_state["result"] = {"findings": findings, "debug": debug, "text": text}

# ---------- 5) 結果表示 ----------
if "result" in st.session_state:
    res = st.session_state["result"]
    st.divider()
    st.markdown("### 3. 解析結果")
    if not res["findings"]:
        st.info("特に強いバイアスは検出されませんでした。バランスの良い判断です。")
    else:
        for f in res["findings"]:
            st.markdown(f"""
            <div class="result-card">
                <h4>{f["label"]}
                    <span class="badge">信頼度: {f["confidence"]}</span>
                    <span class="badge">スコア: {f["score"]}</span>
                </h4>
                <div class="explain">{f["explain"]}</div>
                <b>根拠:</b> {'、'.join(f["evidence"]) if f["evidence"] else 'なし'}<br>
                <b>対策のヒント:</b>
            </div>
            """, unsafe_allow_html=True)
            for tip in f["suggestions"]:
                st.write("・" + tip)

    with st.expander("スコア詳細（上級者向け）"):
        st.write(res["debug"])

    if st.button("結果をクリアしてやり直す"):
        st.session_state.pop("result", None)
        st.rerun()

