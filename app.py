# -*- coding: utf-8 -*-
import json, os
from datetime import datetime
import pandas as pd
import streamlit as st

import streamlit as st
from ui_components import hero, info_cards, stepper
# 既存ロジックは2ページ目で使う想定。ここは導入と入力のみ。

st.set_page_config(page_title="Bias Audit Lab", page_icon="🧠", layout="centered")

# セッション初期化
for k, v in {
    "user_input": "",
    "context_tag": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

hero(
    title="あなたの“思い込み”、AIで見抜ける？",
    subtitle="心理学×行動経済学で、あなたの判断に潜むバイアスをやさしく可視化します。",
    cta_label="解析を試す",
    cta_anchor="#start"
)

stepper(steps=["導入", "入力", "解析"], active=2)

st.markdown("### システム1・システム2って？")
info_cards([
    {
        "icon": "⚡️",
        "title": "システム1（直感）",
        "desc": "速い・自動・省エネ。だけど思い込みの影響を受けやすい。"
    },
    {
        "icon": "🧩",
        "title": "システム2（熟考）",
        "desc": "ゆっくり・論理的・エネルギー消費大。面倒でサボりがち。"
    }
])

st.markdown("### 行動経済学って？")
info_cards([
    {"icon":"😵‍💫","title":"損失回避","desc":"同じ額でも、失う痛みは得る喜びの2倍。"},
    {"icon":"🎯","title":"確証バイアス","desc":"自分の信じたい情報ばかり集めてしまう。"},
    {"icon":"🏷️","title":"アンカリング","desc":"最初に見た数字が、その後の判断を引っ張る。"},
])

st.markdown("### 日常はバイアスだらけ")
st.caption("ニュースの読み方、買い物、投資、進路や仕事の判断…“無意識のクセ”が入ります。だからこそ、いったん点検してみよう。")

st.markdown("<div id='start'></div>", unsafe_allow_html=True)
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
        submit = st.form_submit_button("解析ページへ進む ▶️")

if submit:
    st.session_state["user_input"] = topic.strip()
    st.session_state["context_tag"] = context_tag if context_tag != "未選択" else ""
    if not st.session_state["user_input"]:
        st.warning("まずは内容を1行でも入力してください。")
    else:
        # Streamlitの標準マルチページ遷移（pages/1_解析.pyが表示されます）
        st.switch_page("pages/1_解析.py")


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





st.set_page_config(page_title="バイアス監査アプリ", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
h1 {font-size:1.6rem !important; text-align:center; margin-bottom:0.2em;}
.subtitle {text-align:center; font-size:0.9rem; color:#6c757d;}
.process {text-align:center; font-size:0.85rem; background:#f8f9fa; border-radius:8px; padding:0.4em; margin:0 0 1.2em 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🧠 バイアス監査アプリ")
st.markdown('<div class="subtitle">Self-Bias Monitor (MVP)</div>', unsafe_allow_html=True)
st.markdown('<div class="process">① 入力 → ② 解析 → ③ 介入 → ④ 支援 → ⑤ 保存</div>', unsafe_allow_html=True)

# ========= ルール読み込み =========
@st.cache_data
def load_rules():
    with open("rules.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ========= “弱い表現”も拾うための補助辞書 =========
SOFT_CUES = {
    "loss_aversion": ["損をする気", "後悔しそう", "逃すと", "安くなっているのに", "失うのが怖", "もったいない気"],
    "status_quo": ["今のままでいい", "変える必要", "面倒だから", "慣れているから", "とりあえずこのまま"],
    "anchoring": ["定価が", "参考価格", "最初に見た", "言い値"],
    "present_bias": ["今すぐ欲しい", "先延ばし", "後で考える"],
    "sunk_cost": ["ここまでやった", "元を取りたい", "やめるのは惜しい"],
    "overconfidence": ["絶対いける", "間違いない", "必ず成功", "自分なら大丈夫"],
}
EMOTION_WORDS = ["不安", "心配", "焦る", "怖い", "落ち着かない", "迷う", "混乱", "ドキドキ", "モヤモヤ", "悩む"]
SOFT_CUES["loss_aversion"] += ["逃したくない", "値上げ前に", "限定"]
SOFT_CUES["status_quo"]   += ["現状のまま", "いつも通り"]
SOFT_CUES["anchoring"]    += ["割引前価格", "通常価格"]
SOFT_CUES["sunk_cost"]    += ["もったいない", "ここまで続けた"]


# ========= 解析本体 =========
def analyze_text(text: str, rules: dict, sensitivity: int):
    text = (text or "").strip()
    if not text:
        return [], {}

    # しきい値：1.20（厳）〜0.40（敏感）に線形可変
    threshold = 1.20 - (sensitivity / 100) * 0.80

    findings, debug_scores = [], {}

    # 強シグナル（rules.json）+ 弱シグナル（SOFT_CUES）の合算スコア
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
                "type": key,
                "label": spec.get("label", key),
                "confidence": conf,
                "evidence": evidences,
                "suggestions": spec.get("interventions", []),
                "score": round(score, 2)
            })
            debug_scores[spec.get("label", key)] = round(score, 2)

    # 感情ヒューリスティック（弱い表現も拾う）
    emo_hits = [w for w in EMOTION_WORDS if w in text]
    emo_score = 0.5 * len(emo_hits)  # 1語=0.5点
    if emo_score >= max(0.5, threshold * 0.6):
        findings.append({
            "type": "affect",
            "label": "感情ヒューリスティック",
            "confidence": "B" if emo_score < (threshold + 0.8) else "A",
            "evidence": emo_hits,
            "suggestions": [
                "気持ちが落ち着いてから再評価（24時間ルール）",
                "％や印象を金額・時間に置き換えて比較する",
                "第三者の短評（外部視点）を3行で書く"
            ],
            "score": round(emo_score, 2)
        })
        debug_scores["感情ヒューリスティック"] = round(emo_score, 2)

    findings.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return findings, {"threshold": round(threshold, 2), "scores": debug_scores}

def save_decision(row, path="decisions.csv"):
    df_new = pd.DataFrame([row])
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False, encoding="utf-8-sig")

# ========= ヘッダー =========

with st.expander("設定（任意）", expanded=False):
    st.caption("検出の敏感さ（高いほど拾いやすい）")
    sensitivity = st.slider("検出の敏感さ", 0, 100, 75)
rules = load_rules()

# ========= 1. かんたん入力（3段階プリセット） =========
st.header("1. かんたん入力（選択式）")

theme = st.radio("テーマを選ぶ", ["家計・お金", "仕事・キャリア", "学び・自己成長", "ライフスタイル", "人間関係"], horizontal=True)

if theme == "家計・お金":
    situation = st.selectbox("状況を選ぶ", ["買うか迷う", "続けるかやめる", "固定費/値上げへの対応", "投資の方針"])
    scenarios_map = {
        "買うか迷う": [
            "PCを買う", "スマホ買い替え", "大型家電を買う", "家具を買い替える",
            "趣味アイテムを買う", "旅行を予約する"
        ],
        "続けるかやめる": [
            "動画サブスクの継続", "クラウドソフトの有料プラン", "英語アプリの年払い",
            "習い事の継続", "ジム会員の更新"
        ],
        "固定費/値上げへの対応": [
            "電気・ガスのプラン見直し", "通信費(スマホ/光)を見直す", "保険の更新/乗り換え",
            "定期券/通学定期の更新", "賃貸の更新と家賃交渉"
        ],
        "投資の方針": [
            "インデックス積立を増やす", "個別株を新規に買う", "積立を一旦止める",
            "外貨/金に分散する", "NISA枠の配分を変える"
        ],
    }
    default_options_map = {
        "買うか迷う": "今すぐ買う, 少し待つ, 今回は見送る",
        "続けるかやめる": "継続する, プランを下げる, 一旦解約する",
        "固定費/値上げへの対応": "現状維持, 代替プランを比較して乗り換え, 使い方を減らす",
        "投資の方針": "実行する, 少額から試す, 見送る"
    }
    default_options = default_options_map[situation]
elif theme == "仕事・キャリア":
    situation = st.selectbox("状況を選ぶ", ["転職を考える", "社内異動/担当変更", "学習/資格の投資", "業務の導入/外注"])
    scenarios_map = {
        "転職を考える": [
            "転職活動を始める", "エージェントに登録する", "副業を並行する",
            "研究職から実務職へ移る", "大学院進学に切り替える"
        ],
        "社内異動/担当変更": [
            "希望部署に異動申請", "担当業務の比重を変える", "研究テーマを変更する",
            "TA/RAの配分を変える"
        ],
        "学習/資格の投資": [
            "資格講座に申込む", "学び直しを始める", "英語学習を強化",
            "統計/プログラミングを学ぶ", "国際会議の準備をする"
        ],
        "業務の導入/外注": [
            "新ツールを導入", "プロセスを簡素化", "外注を使う",
            "自動化スクリプトを作る", "チーム標準を策定する"
        ],
    }
    default_options = "始める, 情報を集めてから, 見送る"
elif theme == "学び・自己成長":
    situation = st.selectbox("状況を選ぶ", ["学びを始める/再開", "留学/奨学金を検討", "習慣化したい", "研究テーマ/卒論"])
    scenarios_map = {
        "学びを始める/再開": [
            "オンライン講座に申込む", "週3で学習する", "ゼミ/読書会に参加",
            "MOOCを完走する", "学習記録を毎日つける"
        ],
        "留学/奨学金を検討": [
            "短期留学に行く", "交換留学に応募", "Erasmus Mundusに出願",
            "語学集中プログラムに参加"
        ],
        "習慣化したい": [
            "毎日30分の読書", "朝活を始める", "運動を週3回",
            "SNS時間を制限する", "論文要約を日次で残す"
        ],
        "研究テーマ/卒論": [
            "テーマをピボットする", "先行研究を30本読む", "データ収集計画を立てる",
            "指導教員に方針相談する"
        ],
    }
    default_options = "始める, 小さく試す, 見送る"
elif theme == "ライフスタイル":
    situation = st.selectbox("状況を選ぶ", ["住まい/引っ越し", "健康/運動/睡眠", "時間管理/デジタル", "家事/育児の分担"])
    scenarios_map = {
        "住まい/引っ越し": [
            "引っ越しを検討", "家賃交渉をする", "家具家電を整理する",
            "同棲/実家に戻る"
        ],
        "健康/運動/睡眠": [
            "運動を始める", "夜更かしをやめる", "間食を減らす",
            "睡眠時間を一定にする"
        ],
        "時間管理/デジタル": [
            "SNS時間を減らす", "ポモドーロを導入", "Notion/手帳を一本化",
            "週末はデジタル断食にする"
        ],
        "家事/育児の分担": [
            "家事分担の話し合い", "外部サービスの活用", "週次のタスク表を作る"
        ],
    }
    default_options = "始める, 小さく試す, 見送る"
else:  # 人間関係
    situation = st.selectbox("状況を選ぶ", ["SNS/発信の距離感", "家族/友人との関係", "研究室/職場のコミュニケーション"])
    scenarios_map = {
        "SNS/発信の距離感": [
            "SNSの使い方を見直す", "ポスト頻度を下げる", "DMの通知を切る",
            "リプライ方針を決める"
        ],
        "家族/友人との関係": [
            "距離をとる", "話し合いの場を作る", "定期連絡の頻度を決める",
            "贈り物/お礼の頻度を見直す"
        ],
        "研究室/職場のコミュニケーション": [
            "ミーティング頻度を調整", "依頼の断り方を決める", "相談相手を増やす",
            "フィードバックのルールを作る"
        ],
    }
    default_options = "そのまま続ける, 小さく試す, 見送る"

# セグメントコントロール（古い環境対策：無ければradio）
seg = getattr(st, "segmented_control", None)
scenarios = scenarios_map[situation]
scenario = seg("具体例を選ぶ", scenarios) if seg else st.radio("具体例を選ぶ", scenarios, horizontal=True)

def build_preview(theme, situation, scenario):
    base = ""
    if theme == "家計・お金":
        if situation == "買うか迷う":
            base = f"{scenario}を検討しています。良い条件に感じる一方で、無駄遣いになる不安もあり迷っています。"
        elif situation == "続けるかやめる":
            base = f"{scenario}べきか迷っています。ここまで続けた流れと費用対効果のどちらを重視するかで揺れています。"
        elif situation == "固定費/値上げへの対応":
            base = f"{scenario}ことを検討しています。値上げの影響と、代替プランの比較で判断したいです。"
        elif situation == "投資の方針":
            base = f"{scenario}か迷っています。期待リターンと変動リスクのバランスを整理したいです。"
    elif theme == "仕事・キャリア":
        if situation == "業務の導入/外注":
            base = f"{scenario}ことを考えています。導入コストと習熟の負担、得られる効率化のバランスで迷っています。"
        else:
            base = f"{scenario}かどうか迷っています。将来の選択肢を広げるか、現状維持の安心を取るかで揺れています。"
    elif theme == "学び・自己成長":
        if situation == "留学/奨学金を検討":
            base = f"{scenario}を考えています。費用と得られる機会のどちらを優先するかで迷っています。"
        else:
            base = f"{scenario}を始めるか迷っています。継続できる計画と優先順位を考えたいです。"
    elif theme == "ライフスタイル":
        if situation == "住まい/引っ越し":
            base = f"{scenario}か迷っています。費用・通学/通勤・生活の満足度のバランスで判断したいです。"
        else:
            base = f"{scenario}を検討しています。健康や時間の使い方への影響を踏まえて考えたいです。"
    else:  # 人間関係
        base = f"{scenario}について迷っています。自分と相手の負担や関係性への影響を整理したいです。"

    return base + "\n判断材料や代替案も考慮したいです。"


# === プレビュー用の下ごしらえ（seedでリセット）===
seed = (theme, situation, scenario)
if st.session_state.get("preview_seed") != seed:
    st.session_state["preview_text_value"] = build_preview(theme, situation, scenario)
    st.session_state["preview_opts_value"] = default_options
    st.session_state["preview_seed"] = seed


# ── ここから置き換え ───────────────────────────────
# プレビュー表示用のカラム（左：本文プレビュー／右：選択肢＋反映ボタン）
colA, colB = st.columns([3, 2])

with colA:
    preview_text = st.text_area(
        "自動生成プレビュー（編集可）",
        height=140,
        key="preview_text_value",   
    )

with colB:
    preview_opts = st.text_input(
        "選択肢（カンマ区切り）",
        key="preview_opts_value",   
    )
    if st.button("この内容を下の入力欄へ反映", use_container_width=True, key="reflect_btn_preview"):
        st.session_state["main_decision_text"] = st.session_state.get("preview_text_value", "")
        st.session_state["main_options"] = st.session_state.get("preview_opts_value", "")
        st.success("入力欄へ反映しました。")
# ── 置き換えはここまで ─────────────────────────────

st.header("2. 今日の意思決定（入力）")
decision_text = st.text_area(
    "本文（上の反映で自動入力されます）",
    value=st.session_state.get("main_decision_text", ""),
    height=180,
    key="main_decision_text",   # ← こちらは main_〜 なので重複しません
)

# テキスト入力から「選択肢」をリスト化（multiselect が無い構成のため）
opts_source = st.session_state.get("preview_opts_value") or st.session_state.get("main_options", "")
selected = [o.strip() for o in opts_source.split(",") if o.strip()]



