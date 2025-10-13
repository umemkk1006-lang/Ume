import streamlit as st

selected = st.session_state.get("selected", [])  
import os, json
import pandas as pd


from ui_components import stepper, result_badge, tip_card
# from core.analysis import analyze_text, explain_biases, suggest_debias_nudges

# ===== 受け取った本文 =====
text = st.session_state.get("user_input", "").strip()
if not text:
    st.info("トップページで内容を入力してください。")
    st.page_link("app.py", label="← トップに戻る", icon="🏠")
    st.stop()

st.set_page_config(page_title="解析 - Bias Audit Lab", page_icon="🧪", layout="wide")

st.page_link("app.py", label="← トップへ戻る", icon="🏠")

# 入力チェック
text = st.session_state.get("user_input", "").strip()
if not text:
    st.info("トップページで内容を入力してからお越しください。")
    st.page_link("app.py", label="← トップに戻る", icon="🏠")
    st.stop()

stepper(steps=["導入", "入力", "解析"], active=3)

st.markdown("### 入力内容")
st.write(text)
if st.session_state.get("context_tag"):
    st.caption(f"カテゴリ: {st.session_state['context_tag']}")

st.divider()

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


if st.button("解析する", type="primary"):
    # ====== ここをあなたの解析処理に置き換え ======
    # 例）findings = calc_findings(inputs)  # list を返す。未検出なら []
    findings = []  # 仮：今回は未検出だったケース
    debug_info = {"threshold": "-", "scores": {}}
    # ================================================
    st.session_state.findings = findings or []     # 空でもリストを保存
    st.session_state.debug = debug_info
    st.success("解析しました。下の結果をご確認ください。")

# --- session_state の初期化 ---
if "findings" not in st.session_state:
    st.session_state.findings = None   # None=未実行, []=未検出, ["..."]=検出あり
if "debug" not in st.session_state:
    st.session_state.debug = {}

# 確からしさ(A/B/C)を文字と説明に変換
def confidence_letter(score: float):
    if score >= 0.8:
        return "A", "高い（かなり当てはまりそう）"
    elif score >= 0.6:
        return "B", "中くらい（それっぽいが他の可能性も）"
    else:
        return "C", "低め（参考程度）"

# 1件分のカード表示
def render_finding_card(f: dict):
    label = f.get("label", "（名称未設定）")
    score = float(f.get("score", 0.0) or 0.0)
    letter, expl = confidence_letter(score)

    with st.container(border=True):
        st.markdown(f"**{label}**　|　確からしさ：**{letter}**（{expl}）")

        ev = f.get("evidence") or []
        if ev:
            st.caption("根拠：" + "、".join(ev[:3]))
        with st.expander("対処ヒントを見る"):
            for s in f.get("suggestions", []):
                st.markdown("- " + s)


# ======== 3. 解析結果 ========
st.header("3. 解析結果")

findings = st.session_state.get("findings", None)  # ← 既定を None に
dbg = st.session_state.get("debug", {})

if findings is None:
    # まだ解析を押していない
    st.caption("（解析未実行）")

elif len(findings) == 0:
    # 解析はしたがヒットなし → ここで褒める＆次導線
    st.success("🎉 今回は偏りは見つかりませんでした。落ち着いた判断ができていますね。")
    st.info("次は「4. 介入の選択と記入」または「4️⃣ 支援介入」で、現実的な行動プランを作りましょう。")

else:
   for f in findings:
    render_finding_card(f)

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
