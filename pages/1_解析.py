# -*- coding: utf-8 -*-
# pages/1_解析.py

import os, json
import streamlit as st

# ========= 解析ロジック（UIより上に置く！） =========

# ソフトなシグナル（弱い示唆語）
SOFT_CUES = {
    "confirmation": ["確信", "間違いない", "絶対", "都合の良い", "見たいものだけ"],
    "sunk_cost": ["せっかく", "ここまでやった", "元を取る", "もったいない"],
    "loss_aversion": ["損したくない", "無駄", "不安", "なくす", "後悔"],
    "availability": ["よく聞く", "みんな言ってる", "SNSで見た", "バズってる"],
    "framing": ["お得", "割引", "限定", "今だけ", "先着"],
}

# 感情ヒューリスティック用の簡易語彙
EMOTION_WORDS = ["不安", "焦り", "ワクワク", "怖い", "嬉しい", "悔しい", "怒り", "緊張"]

# rules.json を読めなければデフォルトルールを使う
def load_rules() -> dict:
    default_rules = {
        "confirmation": {
            "label": "確証バイアス",
            "keywords": ["自分の考えに合う", "都合が良い", "反対の情報を無視"],
            "interventions": [
                "反対の証拠を最低1つ探す",
                "立場が逆の人になりきって主張を書いてみる",
            ],
        },
        "sunk_cost": {
            "label": "サンクコストの誤謬",
            "keywords": ["ここまで投資", "もったいない", "元を取る", "諦めない"],
            "interventions": [
                "今から始めるとしても同じ判断をするか？を自問",
                "未来の利益/損失だけで比較する",
            ],
        },
        "loss_aversion": {
            "label": "損失回避バイアス",
            "keywords": ["損したくない", "失う", "無駄になる"],
            "interventions": [
                "損失だけでなく得られる価値も横並びで書き出す",
                "金額ではなく目的（何のため？）で評価する",
            ],
        },
        "availability": {
            "label": "利用可能性ヒューリスティック",
            "keywords": ["よく聞く", "SNSで見た", "話題", "バズり"],
            "interventions": [
                "一次情報（元データ/一次ソース）を1つ確認する",
                "最近見た事例と統計的な頻度を区別する",
            ],
        },
        "framing": {
            "label": "フレーミング効果",
            "keywords": ["お得", "割引", "今だけ", "限定", "先着", "在庫わずか"],
            "interventions": [
                "同じ内容を別表現（損失表示/確率表示）に言い換えて検討",
                "長期的な総コスト/リスクで比較する",
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
    """
    簡易ルールベース解析。
    sensitivity: 0〜100（高いほど検知しやすい）。しきい値は線形で可変。
    戻り値: (findings(list[dict]), debug_scores(dict))
    """
    text = (text or "").strip()
    if not text:
        return [], {}

    # しきい値: 1.20(厳)〜0.40(敏感) の間で線形
    threshold = 1.20 - (sensitivity / 100) * 0.80
    findings, debug_scores = [], {}

    for key, spec in rules.items():
        score, evidences = 0.0, []

        # 強めシグナル（キーワード）
        for kw in spec.get("keywords", []):
            if kw and kw in text:
                score += 1.0
                evidences.append(kw)

        # 弱めシグナル（SOFT_CUES）
        for soft_kw in SOFT_CUES.get(key, []):
            if soft_kw and soft_kw in text:
                score += 0.5
                evidences.append(soft_kw)

        if score >= threshold:
            conf = "A" if score >= (threshold + 0.8) else "B"
            findings.append({
                "type": key,
                "label": spec.get("label", key),
                "confidence": conf,
                "evidence": evidences,
                "suggestions": spec.get("interventions", []),
                "score": round(score, 2),
            })
        debug_scores[spec.get("label", key)] = round(score, 2)

    # 感情ヒューリスティック（おまけ）
    emo_hits = [w for w in EMOTION_WORDS if w in text]
    emo_score = 0.5 * len(emo_hits)
    if emo_score >= max(0.5, threshold * 0.6):
        findings.append({
            "type": "affect",
            "label": "感情ヒューリスティック",
            "confidence": "B" if emo_score < (threshold + 0.8) else "A",
            "evidence": emo_hits,
            "suggestions": [
                "一晩おいてから再評価（24時間ルール）",
                "第三者の短評（外部視点）を3行でもらう",
            ],
            "score": round(emo_score, 2),
        })
    debug_scores["感情ヒューリスティック"] = round(emo_score, 2)

    findings.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return findings, {"threshold": round(threshold, 2), "scores": debug_scores}

# ========= UI =========

st.set_page_config(page_title="バイアス解析アプリ", layout="centered", initial_sidebar_state="collapsed")

# ちょっとだけ読みやすいCSS（モバイル最適）
st.markdown("""
<style>
h1 { text-align:center; margin-bottom:0.2rem; }
.small { color:#667; font-size:0.9rem; text-align:center; margin-bottom:0.6rem; }
section { background:#fff; border:1px solid #eee; border-radius:12px; padding:0.9rem 1rem; margin:0.6rem 0; }
label, .stRadio, .stSelectbox, .stTextArea { font-size:1rem; }
.result-card { border:1px solid #e8e8e8; border-radius:10px; padding:0.8rem; margin-bottom:0.6rem; background:#fcfcff; }
.kicker { font-size:.9rem; color:#667; margin-bottom:.2rem; }
.badge { display:inline-block; padding:.1rem .5rem; border-radius:999px; background:#eef; margin-left:.4rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧠 バイアス解析アプリ</h1>", unsafe_allow_html=True)
st.markdown('<div class="small">Self-Bias Monitor (MVP)</div>', unsafe_allow_html=True)

# --- 設定（任意） ---
with st.expander("設定（任意）", expanded=False):
    sensitivity = st.slider("検出の敏感さ（高いほど拾いやすい）", 0, 100, value=int(st.session_state.get("sensitivity", 50)))
    st.session_state["sensitivity"] = sensitivity

# --- 1. かんたん入力（選択式） ---
st.markdown("### 1. かんたん入力（選択式）")
themes = {
    "家計・お金": {
        "状況": ["買うか迷う", "契約の更新", "やめるか迷う"],
        "例": ["PCを買う", "スマホ買い替え", "大型家電を買う", "家具を買い替える", "旅行を予約する"],
    },
    "仕事・キャリア": {
        "状況": ["応募するか迷う", "転職を検討", "資格に挑戦"],
        "例": ["転職サイトに登録", "社内公募に応募", "資格の受験申し込み"],
    },
    "学び・自己成長": {
        "状況": ["コース受講を検討", "書籍購入を検討"],
        "例": ["オンライン講座を受ける", "専門書を買う", "勉強会に参加"],
    },
    "人間関係": {
        "状況": ["誘いに乗るか迷う", "連絡すべきか迷う"],
        "例": ["飲み会に参加", "久しぶりに連絡する", "SNSに投稿する"],
    },
    "ライフスタイル": {
        "状況": ["習慣を始める/やめる", "サブスクの見直し"],
        "例": ["ジムに入会", "早起きを始める", "動画サブスクを解約"],
    },
}

colA, colB = st.columns(2)
with colA:
    theme = st.radio("テーマを選ぶ", list(themes.keys()), horizontal=False, index=0, key="theme")
with colB:
    status = st.selectbox("状況を選ぶ", themes[st.session_state["theme"]]["状況"], key="status")

example = st.selectbox("具体例を選ぶ", themes[st.session_state["theme"]]["例"], key="example")

# プレビュー自動生成
preview = f"{example} を検討しています。良い条件に感じる一方で、不安や無駄遣いになる不安もあり迷っています。判断材料や代替案も考慮したいです。"
st.text_area("自動生成プレビュー（編集可）", value=preview, key="preview_text", height=110)

# --- 2. 今日の意思決定（入力） ---
st.markdown("### 2. 今日の意思決定（入力）")
default_text = st.session_state.get("user_input", st.session_state.get("preview_text", ""))
decision_text = st.text_area("本文（上のプレビューから自由に編集してください）", value=default_text, key="decision_text", height=160)

# --- 3. バイアス解析 ---
st.markdown("### 3. バイアス解析")
run = st.button("バイアス解析", type="primary", use_container_width=True)

if run:
    txt = (st.session_state.get("decision_text") or "").strip()
    if not txt:
        st.warning("本文が空です。上の入力欄に内容を書いてください。")
    else:
        with st.spinner("解析中..."):
            findings, debug = analyze_text(txt, RULES, st.session_state.get("sensitivity", 50))
        st.session_state["analysis_result"] = {"findings": findings, "debug": debug, "text": txt}

# 解析結果の表示（ボタン後、またはセッションに残っていれば表示）
res = st.session_state.get("analysis_result")
if res:
    st.divider()
    st.subheader("解析結果")
    if not res["findings"]:
        st.info("明確なバイアスは検出されませんでした。")
    else:
        for f in res["findings"]:
            with st.container():
                st.markdown(
                    f"""
                    <div class="result-card">
                      <div class="kicker">検出タイプ</div>
                      <h4 style="margin:.2rem 0 .4rem 0;">{f.get('label','(不明)')}
                        <span class="badge">信頼度: {f.get('confidence','-')}</span>
                        <span class="badge">スコア: {f.get('score','-')}</span>
                      </h4>
                    """,
                    unsafe_allow_html=True,
                )
                if f.get("evidence"):
                    st.caption("根拠: " + "、".join(f["evidence"]))
                tips = f.get("suggestions", [])
                if tips:
                    st.markdown("**バイアス低減のヒント**")
                    for t in tips:
                        st.write("・" + t)
                st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("デバッグ（スコア詳細）", expanded=False):
        st.write("しきい値:", res["debug"].get("threshold"))
        st.write(res["debug"].get("scores", {}))

    st.markdown("")
    if st.button("結果をクリアしてやり直す"):
        for k in ["analysis_result"]:
            st.session_state.pop(k, None)
        st.experimental_rerun()
