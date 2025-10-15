# -*- coding: utf-8 -*-
# pages/1_解析.py

import os, json
import streamlit as st

# ---- Hero / Page header (復元) ----
st.markdown("""
<style>
/* タイトルをモバイル向けに少し小さく */
h1.hero-title { 
  font-size: 1.55rem; 
  margin: .2rem 0 .3rem; 
  text-align: center;
}
.hero-sub { 
  text-align:center; 
  color:#6c757d; 
  font-size:.95rem; 
  margin-bottom:.6rem;
}
/* セクション見出しも少し控えめに */
h2, h3 { font-size: 1.1rem; margin: .7rem 0 .35rem; }
</style>

<h1 class="hero-title">🧠 バイアス解析アプリ</h1>
<div class="hero-sub">Self-Bias Monitor (MVP)</div>
""", unsafe_allow_html=True)


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

# --- 必須インポート（ページ冒頭） ---
import streamlit as st
from datetime import datetime

# ------ セッション初期化 ------
for k, v in {
    "decision_text": "",        # 入力欄の本文
    "easy_theme": "お金・家計",
    "easy_situation": "買うか迷う",
    "easy_example": "",
    "easy_preview": "",         # プレビュー文
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------ CSS：スマホで見やすいサイズを強制適用 ------
st.markdown("""
<style>
/* Streamlit は内部で h1,h2 に別の余白/サイズを当てるため、スコープ広めに指定 */
.stApp div.block-container h1 {
  font-size: 1.25rem;           /* ← タイトル小さめ */
  line-height: 1.35;
  margin: .6rem 0 .4rem 0;
}
.stApp div.block-container h2 {
  font-size: 1.05rem;
  margin: .9rem 0 .45rem 0;
}
.small-note { font-size:.85rem; color:#666; }
.preview-card{
  border:1px solid #e9e9ee; border-radius:10px; padding:.8rem; background:#fafbff;
}
</style>
""", unsafe_allow_html=True)

# ========================
# 1. かんたん入力（選択式）
# ========================

# セッション初期化（なければ）
for k, v in {
    "easy_theme": None,
    "easy_situation": None,
    "easy_example": None,
    "easy_preview": "",
    "decision_text": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("### 1. かんたん入力（選択式）")
st.caption("※ テーマ → 状況 → 具体例 を選ぶと、下に文章が自動生成されます。必要なら編集して『この内容を下の入力欄へ反映』を押してください。")

# --- マスタ定義（20代会社員を想定） ---
THEMES = ["お金・家計", "仕事・キャリア", "スキル・学習", "人間関係（職場）", "健康・生活リズム", "住まい・暮らし"]

SITUATIONS = {
    "お金・家計": ["買うか迷う", "契約やサブスクを見直す", "投資や貯金の判断"],
    "仕事・キャリア": ["転職・異動を考える", "資格取得するか", "残業や業務の優先順位"],
    "スキル・学習": ["学習計画を立てる", "教材やスクールを選ぶ", "継続するか中断するか"],
    "人間関係（職場）": ["上司への相談", "同僚への依頼", "会議での発言"],
    "健康・生活リズム": ["運動や睡眠の見直し", "食事・間食のコントロール", "通院・検査の判断"],
    "住まい・暮らし": ["家具・家電の買い替え", "引っ越しを検討", "固定費の節約"]
}

# 具体例（テーマ×状況ごとのテンプレ文）
EXAMPLES = {
    ("お金・家計", "買うか迷う"): [
        "PCを買う／良い条件に感じるが無駄遣いになる不安もある。判断材料や代替案も考えたい。",
        "スマホを買い替える／今の端末でも使えるが、カメラやバッテリーに不満がある。",
        "大型家電を買う／セールで安いが本当に必要か迷っている。"
    ],
    ("お金・家計", "契約やサブスクを見直す"): [
        "動画サブスクを解約するか迷う。あまり見ていないが解約が面倒に感じる。",
        "保険の見直し／特約を付けるべきか、今のままで良いか判断したい。"
    ],
    ("仕事・キャリア", "転職・異動を考える"): [
        "今の部署に残るか、異動希望を出すか迷っている。メリット・デメリットを整理したい。",
        "転職サイトに登録するか判断したい。情報収集が先か、動くべきか迷う。"
    ],
    ("スキル・学習", "教材やスクールを選ぶ"): [
        "英語学習の教材をどれにするか迷う。費用対効果と継続しやすさを比較したい。"
    ],
    ("人間関係（職場）", "会議での発言"): [
        "会議で反対意見を言うべきか迷う。場の空気と建設的な提案のバランスを取りたい。"
    ],
    ("健康・生活リズム", "運動や睡眠の見直し"): [
        "就寝時間が遅い。改善策を小さく始めたい。",
        "運動を週2回に増やしたいが続くか不安。"
    ],
    ("住まい・暮らし", "家具・家電の買い替え"): [
        "仕事用チェアを買い替える。価格と体への負担軽減のバランスを見たい。"
    ],
}

# --- UI（1カラムでシンプルに） ---
theme = st.radio("テーマを選ぶ", THEMES, horizontal=True, key="easy_theme")

sits = SITUATIONS.get(theme, [])
situation = st.selectbox("状況を選ぶ", sits, key="easy_situation")

examples = EXAMPLES.get((theme, situation), [])
example = st.selectbox("具体例", examples or ["（該当の具体例がありません）"], key="easy_example")

# --- プレビュー生成 ---
def make_preview(theme: str, situation: str, example: str) -> str:
    base = example if example and "（該当" not in example else ""
    if not base:
        return ""
    return f"{base}\n判断材料を整理し、短期と長期の視点の両方から検討したいです。"

st.markdown("#### 自動生成プレビュー（編集可）")
st.session_state.easy_preview = make_preview(theme, situation, example)
st.session_state.easy_preview = st.text_area(
    " ",                      # ラベルは空でスッキリ
    value=st.session_state.easy_preview,
    height=130,
    key="easy_preview_area"
)

# --- 入力欄（本文）へ反映 ---
col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("この内容を下の入力欄へ反映", use_container_width=True):
        st.session_state["decision_text"] = st.session_state.easy_preview
        st.success("反映しました。下の『2. 今日の意思決定（入力）』をご確認ください。")
with col_b:
    st.caption("※ 反映後も自由に加筆修正できます。")

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

