# -*- coding: utf-8 -*-
import json, os
from datetime import datetime
import pandas as pd
import streamlit as st
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


if "プレモーテム" in selected:
    premortem = st.text_area("プレモーテム：最悪結果の主因Top3と予防策（各1行）", height=120, key="premortem")

if "外部視点" in selected:
    cA, cB, cC = st.columns(3)
    with cA: outside_A = st.text_area("Aさんの3行コメント", height=90, key="outside_A")
    with cB: outside_B = st.text_area("Bさんの3行コメント", height=90, key="outside_B")
    with cC: outside_C = st.text_area("Cさんの3行コメント", height=90, key="outside_C")

if "ベースレート確認" in selected:
    base_rate_source = st.text_input("出典URLや資料名（なければ『なし』）", value="", key="base_rate")

if "フレーミング反転（％→円/損失）" in selected:
    framing = st.text_input("反転後の表現（例：年◯円の損失に相当 など）", value="", key="framing")

if "決定遅延（24h後に再確認）" in selected:
    delay_24h = st.toggle("24時間後に再確認（端末側のリマインダ設定を推奨）", value=True, key="delay24h")

c1, c2 = st.columns(2)
with c1:
    importance = st.slider("重要度", 0, 100, 50)
with c2:
    confidence_pre = st.slider("自信度（介入前）", 0, 100, 50)

if st.button("解析する", type="primary", use_container_width=True):
    if not decision_text.strip():
        st.warning("本文を入力してください（上の『反映』ボタンが便利です）")
    else:
        findings, dbg = analyze_text(decision_text, rules, sensitivity)
        st.session_state["findings"] = findings
        st.session_state["debug"] = dbg
        st.session_state["decision_text"] = decision_text
        st.session_state["options_text"] = st.session_state.get("preview_opts_value", "")
        st.session_state["importance"] = importance
        st.session_state["confidence_pre"] = confidence_pre
        st.success("解析しました。下の結果をご確認ください。")

# ========= 3. バイアス検知（候補） =========
st.header("3. バイアス検知（候補）")
findings = st.session_state.get("findings", [])
dbg = st.session_state.get("debug", {})
if findings:
    st.caption(f"内部しきい値: {dbg.get('threshold','-')} / スコア: {dbg.get('scores',{})}")
    for f in findings:
        with st.container(border=True):
            st.subheader(f"{f['label']}（確度{f['confidence']}）")
            if f.get("score") is not None:
                st.caption(f"内部スコア：{f['score']}")
            st.write("根拠：", "、".join(f["evidence"]) if f["evidence"] else "（自動推定）")
            with st.expander("このバイアスへの介入案を表示"):
                for s in f.get("suggestions", []):
                    st.markdown(f"- {s}")
else:
    st.caption("（解析未実行 or ヒットなし）")

# 4. =========介入の選択と記入=========

st.header("4. 介入の選択と記入")

# 既定値（無い場合は空）をセッションから取り出す（必要なら）
_selected_default = st.session_state.get("selected", [])

options = {
    "外部視点": "第三者や未来の自分の視点で見直す",
    "ベースレート確認": "統計や過去の確率に照らして再考する",
    "フレーミング反転": "損得の表現を入れ替えて評価する",
    "決定遅延": "24時間置いてから再評価する",
    "プレモーテム": "失敗を仮定して原因と予防策を先に考える",
}

selected = st.multiselect(
    "実施する介入（最大2つ）",
    list(options.keys()),
    max_selections=2,
    default=_selected_default,
    key="selected",
    help="介入＝バイアスを中和する“思考アクション”です。"
)

for k in selected:
    st.caption(f"ℹ️ {k}: {options[k]}")

# プレモーテム選択時の入力欄
if "プレモーテム" in selected:
    st.write("🔍 プレモーテム：最悪結果の主因Top3と予防策（各1行）")
    for i in range(1, 4):
        st.text_input(f"主因{i}", placeholder="例：準備不足")
        st.text_input(f"予防策{i}", placeholder="例：前日にチェックリスト作成")


# -*- coding: utf-8 -*-
# ================================
# 4) 支援介入（現実的な対策）
# ================================
st.subheader("4️⃣ 支援介入（現実的な対策）")
st.caption("不安を具体化すると、現実的な代替案や制度が見つかりやすくなります。")

theme = st.text_input("いまの不安を一言で（例：教育費が心配、住宅ローン、老後が不安）")
income = st.text_input("どのくらいの収入があれば安心？（例：月25万円）")
years = st.number_input("老後まであと何年？", min_value=0, max_value=80, value=20, step=1)
areas = st.multiselect(
    "心配分野（複数選択可）",
    ["教育費", "健康", "住宅ローン", "老後資金", "生活費", "仕事・収入の不安"]
)

def suggest_lines(theme_text: str, areas_selected: list, income_text: str, years_to_retire: int):
    t = theme_text or ""
    tags = set(areas_selected)

    if ("教育" in t) or ("学費" in t) or ("塾" in t):
        tags.add("教育費")
    if ("住宅" in t) or ("ローン" in t) or ("家賃" in t):
        tags.add("住宅ローン")
    if ("老後" in t) or ("年金" in t) or ("退職" in t):
        tags.add("老後資金")
    if ("健康" in t) or ("医療" in t):
        tags.add("健康")
    if ("生活費" in t) or ("家計" in t) or ("節約" in t):
        tags.add("生活費")
    if ("収入" in t) or ("仕事" in t) or ("転職" in t) or ("副業" in t):
        tags.add("仕事・収入の不安")

    base = [
        "支出の見える化：1日10分の家計記録で“見えない支出”を可視化する。",
        "優先順位づけ：今月の『守る支出（必須）／減らす支出（調整）／やめる支出（不要）』を仕分けする。",
        "自治体の相談窓口：お住まいの自治体サイトで生活・教育・住宅等の支援制度を一覧確認する。"
    ]

    bucket = {
        "教育費": [
            "就学援助・奨学金：自治体の就学援助、国・自治体の奨学金（無利子含む）を確認。",
            "学びの代替：無料のオンライン教材・図書館講座・地域学習会を活用して学習効果を維持。",
            "費用の平準化：年額イベント（受験・教材）を月割りで積立、臨時出費を平準化。"
        ],
        "住宅ローン": [
            "控除や軽減：住宅ローン控除、固定資産税の減免・リフォーム補助の適用可否を確認。",
            "返済見直し：金利タイプの見直し・借換え・返済期間の延長短縮の試算を家計アプリで実行。",
            "住居費基準：手取りの25〜30%以内を目標に、基準超過なら契約条件の再交渉や住み替えも検討。"
        ],
        "老後資金": [
            f"制度活用：iDeCo/つみたてNISAなど税優遇制度で長期積立。年金記録のねんきんネット確認。",
            f"年数逆算：老後までの年数（例: {years_to_retire}年）で、月いくら積み立てればよいかを逆算。",
            "つながり維持：地域活動・軽運動・学び直しで健康寿命と社会的つながりを確保。"
        ],
        "健康": [
            "定期検診：自治体の無料/低額検診、健康相談の利用スケジュールを作成。",
            "食・睡眠・運動：お金をかけない生活改善（自炊・就寝前のスマホ断ち・歩数目標）を実施。",
            "医療費対策：高額療養費制度・自立支援医療などの対象可否を確認。"
        ],
        "生活費": [
            "固定費：通信・保険・サブスクの見直しで月◯%削減を狙う。",
            "変動費：食費は週単位の予算袋方式でコントロール（特売日×作り置き）。",
            "公共サービス：図書館・公園・公共スポーツ施設を積極活用して娯楽費を置き換え。"
        ],
        "仕事・収入の不安": [
            "収入の底上げ：社内の手当・資格手当・評価基準を確認。昇給の道筋を上司と合意。",
            "小さな副業：週2〜3時間で始められるスキル販売/オンライン講座を試行（失敗コストを極小に）。",
            "転職準備：職務経歴の棚卸し→求人票の要件差分を学習計画に変換（3か月単位）。"
        ]
    }

    income_hint = []
    if income_text:
        income_hint.append(f"安心ライン（あなたの目安）：{income_text}。この数字を基準に、毎月の必要貯蓄や稼得計画を逆算。")

    lines = []
    for tag in tags:
        if tag in bucket:
            lines.extend(bucket[tag])

    if not lines:
        lines = base.copy()
    else:
        lines = base + lines

    if income_hint:
        lines = income_hint + lines

    uniq = []
    for x in lines:
        if x not in uniq:
            uniq.append(x)
    return uniq[:6]

if st.button("提案を表示"):
    suggestions = suggest_lines(theme, areas, income, years)
    st.markdown("💡 **あなたへの提案**")
    for s in suggestions:
        st.write("- " + s)
    st.caption("※具体的な名称・要件はお住まいの自治体サイトで必ずご確認ください。")


# ========= 5. 再評価 & 保存 =========
st.header("5. 再評価と保存")
confidence_post = st.slider("自信度（介入後）", 0, 100, 50)
change_reason = st.text_input("自信が変化した理由（100字以内）", value="")

if st.button("この意思決定を保存", use_container_width=True):
    row = {
        "decision_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "theme": theme, "situation": situation, "scenario": scenario,
        "text": st.session_state.get("decision_text", ""),
        "options": st.session_state.get("options_text", ""),
        "importance": st.session_state.get("importance", 0),
        "confidence_pre": st.session_state.get("confidence_pre", 0),
        "biases": ";".join([f"{f['label']}:{f['confidence']}" for f in findings]) if findings else "",
        "evidence": ";".join([",".join(f["evidence"]) for f in findings]) if findings else "",
        "interventions": ";".join(selected),
        "premortem": (premortem or "").replace("\n", " / "),
        "outside_view_A": (outside_A or "").replace("\n", " / "),
        "outside_view_B": (outside_B or "").replace("\n", " / "),
        "outside_view_C": (outside_C or "").replace("\n", " / "),
        "base_rate_source": base_rate_source,
        "framing": framing,
        "delay_24h": delay_24h,
        "confidence_post": confidence_post,
        "change_reason": change_reason
    }
    save_decision(row)
    st.success("保存しました。下の『履歴』で確認できます。")

# ========= 6. 履歴 =========
st.header("6. 履歴")
if os.path.exists("decisions.csv"):
    df = pd.read_csv("decisions.csv")
    st.dataframe(df, use_container_width=True, height=300)
    st.download_button("CSVをダウンロード",
                       data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="decisions.csv", mime="text/csv")
else:
    st.caption("まだ保存はありません。")

st.divider()
st.markdown("© Bias Audit MVP — 学習目的。高リスク判断は専門家の助言も併用してください。")
