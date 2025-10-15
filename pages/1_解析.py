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

# ------ 簡単入力：辞書定義 ------
THEMES = ["お金・家計", "仕事・キャリア", "スキル・学習", "人間関係（職場）", "健康・生活リズム", "住まい・暮らし"]

SITUATIONS = {
    "お金・家計": ["買うか迷う", "固定費を見直す", "貯金/投資を始める"],
    "仕事・キャリア": ["転職を考える", "資格を取る", "副業を始める"],
    "スキル・学習": ["新しい勉強を始める", "勉強時間を増やす", "教材を買うか迷う"],
    "人間関係（職場）": ["頼み事をする", "断る/調整する", "報連相のやり方を変える"],
    "健康・生活リズム": ["運動を始める", "睡眠を整える", "食生活を改善する"],
    "住まい・暮らし": ["引っ越しを考える", "家電を買い替える", "サブスクを解約する"],
}

EXAMPLES = {
    ("お金・家計", "買うか迷う"): ["PCを買う", "スマホ買い替え", "大型家電を買う", "趣味アイテムを買う"],
    ("お金・家計", "固定費を見直す"): ["携帯プラン変更", "保険の見直し", "動画サブスク解約"],
    ("お金・家計", "貯金/投資を始める"): ["つみたてNISA", "定期預金", "iDeCo加入"],

    ("仕事・キャリア", "転職を考える"): ["応募するか迷う", "今の部署で続ける", "上司に相談する"],
    ("仕事・キャリア", "資格を取る"): ["簿記2級", "TOEIC対策", "ITパスポート"],
    ("仕事・キャリア", "副業を始める"): ["ブログ/発信", "動画編集を学ぶ", "プログラミング学習"],

    ("スキル・学習", "新しい勉強を始める"): ["Python入門", "Webデザイン", "統計学"],
    ("スキル・学習", "勉強時間を増やす"): ["朝活を始める", "通勤時間を活用", "学習アプリ導入"],
    ("スキル・学習", "教材を買うか迷う"): ["オンライン講座", "問題集", "有料ノート"],

    ("人間関係（職場）", "頼み事をする"): ["同僚にヘルプ依頼", "上司へ調整依頼", "他部署に相談"],
    ("人間関係（職場）", "断る/調整する"): ["期限延長をお願い", "会議時間の調整", "作業の優先度変更"],
    ("人間関係（職場）", "報連相のやり方を変える"): ["日報の改善", "短い定例ミーティング", "チャット運用ルール"],

    ("健康・生活リズム", "運動を始める"): ["ジムに通う", "自宅トレ", "朝の散歩"],
    ("健康・生活リズム", "睡眠を整える"): ["就寝時間を固定", "寝る前スマホOFF", "寝具の見直し"],
    ("健康・生活リズム", "食生活を改善する"): ["自炊を増やす", "間食を減らす", "飲み物を水にする"],

    ("住まい・暮らし", "引っ越しを考える"): ["職場に近い物件", "家賃を下げる", "シェアハウス"],
    ("住まい・暮らし", "家電を買い替える"): ["冷蔵庫", "洗濯機", "掃除機"],
    ("住まい・暮らし", "サブスクを解約する"): ["動画", "音楽", "ゲーム"],
}

def build_preview(theme:str, situation:str, example:str)->str:
    """選択肢から分かりやすい1〜3文のプレビューを生成"""
    if not (theme and situation):
        return ""
    base = {
        "お金・家計": "お金の使い方で迷っています。",
        "仕事・キャリア": "今後の働き方について考えています。",
        "スキル・学習": "学習の方向性を整理したいです。",
        "人間関係（職場）": "職場でのコミュニケーションについて悩んでいます。",
        "健康・生活リズム": "生活リズムや健康面を整えたいです。",
        "住まい・暮らし": "暮らし方を少し見直したいと思っています。",
    }.get(theme, "")
    ex = f" 今は『{example}』を候補にしています。" if example else ""
    want = " 無駄遣いにならず、後悔しない選択にしたいです。"
    return f"{base} 状況は『{situation}』です。{ex}{want}"

# ------ UI：簡単入力（選択式） ------
st.header("1. かんたん入力（選択式）")
t = st.segmented_control("テーマを選ぶ", THEMES, key="easy_theme")  # Streamlit 1.41+ / 古い場合は radio に変更
if isinstance(t, int):  # 古いバージョン保険
    st.session_state.easy_theme = THEMES[t]

sits = SITUATIONS.get(st.session_state.easy_theme, [])
st.selectbox("状況を選ぶ", sits, key="easy_situation")

ex_list = EXAMPLES.get((st.session_state.easy_theme, st.session_state.easy_situation), [])
cols = st.columns(3)
with cols[0]:
    st.selectbox("具体例", ex_list[:max(1,len(ex_list)//3)], key="easy_example_left")
with cols[1]:
    st.selectbox("　", ex_list[max(1,len(ex_list)//3):max(2,2*len(ex_list)//3)], key="easy_example_mid", label_visibility="collapsed")
with cols[2]:
    st.selectbox("　", ex_list[max(2,2*len(ex_list)//3):], key="easy_example_right", label_visibility="collapsed")

# 3つの箱のどれかに入った値を採用
picked_example = (
    st.session_state.get("easy_example_left")
    or st.session_state.get("easy_example_mid")
    or st.session_state.get("easy_example_right")
    or ""
)
st.session_state.easy_example = picked_example

# プレビューを都度作る
st.session_state.easy_preview = build_preview(
    st.session_state.easy_theme,
    st.session_state.easy_situation,
    st.session_state.easy_example
)

st.caption("自動生成プレビュー（編集可）")
st.text_area("", st.session_state.easy_preview, key="easy_preview_box", height=120)

# 入力欄へ反映
if st.button("この内容を下の入力欄へ反映"):
    st.session_state.decision_text = st.session_state.easy_preview_box
    st.success("反映しました。下の入力欄をご確認ください。")

st.divider()

# ------ 入力欄（本文） ------
st.header("2. 今日の意思決定（入力）")
st.caption("※ 上の反映ボタンで自動入力できます。自由に追記・編集OK。")
st.text_area("本文", st.session_state.decision_text, key="decision_text", height=180)


# ========= 解析ボタン ～ 結果表示 =========

# 解析用ルールを取得（あなたのファイル内の関数名に合わせてください）
try:
    rules = load_rules()         # すでに定義済みの関数
except Exception as e:
    st.error(f"ルールの読み込みに失敗しました: {e}")
    rules = {}

# 解析の感度（0～100）。上で作った slider を流用
sensitivity = int(st.session_state.get("sensitivity", 50))

# ---- 解析実行ボタン ----
if st.button("バイアスを解析する", type="primary", use_container_width=True):
    text = st.session_state.get("decision_text", "") or ""
    if not text.strip():
        st.warning("入力欄が空です。内容を記入してください。")
    else:
        with st.spinner("解析中..."):
            try:
                # あなたの解析関数（既存のものを呼び出します）
                findings, meta = analyze_text(text, rules, sensitivity)
                st.session_state["analysis"] = {
                    "text": text,
                    "findings": findings,  # list[dict]
                    "meta": meta           # {"threshold": float, "scores": {...}} など
                }
                st.success("解析が完了しました。結果を下に表示します。")
            except Exception as e:
                st.error(f"解析でエラーが発生しました: {e}")

st.divider()

# ---- 結果表示 ----
if "analysis" in st.session_state:
    data = st.session_state["analysis"]
    findings = data.get("findings", [])
    meta = data.get("meta", {})

    st.subheader("解析結果")

    if not findings:
        st.info("明確なバイアスは検出されませんでした。")
    else:
        # サマリー（バッジ）
        st.markdown('<div class="badge">検出数：<b>'
                    f'{len(findings)}</b></div>', unsafe_allow_html=True)

        # 各項目をカードで表示
        for i, f in enumerate(findings, 1):
            label = f.get("label", f.get("type", ""))
            conf  = str(f.get("confidence", ""))  # "A" / "B" など
            score = f.get("score", None)
            evs   = f.get("evidence", []) or []
            sugg  = f.get("suggestions", []) or []

            # 見出し
            st.markdown(
                f'<div class="result-card">'
                f'<div class="badge">{i}</div>'
                f'<h3>{label}</h3>'
                f'<div class="tip">自信度：<b>{conf}</b>'
                + (f' ・ スコア：<b>{score}</b>' if score is not None else '')
                + '</div>',
                unsafe_allow_html=True
            )

            # 根拠・ヒント
            if evs:
                st.markdown("**検出キーワード（根拠）**")
                st.markdown("、".join([f"`{e}`" for e in evs]))
            if sugg:
                st.markdown("**試してみること（介入）**")
                for s in sugg:
                    st.markdown(f"- {s}")

            st.markdown("</div>", unsafe_allow_html=True)  # .result-card を閉じる

    # デバッグ（任意）
    with st.expander("デバッグ（スコア詳細）"):
        th = meta.get("threshold")
        scores = meta.get("scores", {})
        if th is not None:
            st.caption(f"しきい値：{th}")
        if scores:
            # スコアを降順で見やすく
            ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            st.table({"指標": [k for k, _ in ordered],
                      "スコア": [round(v, 2) for _, v in ordered]})
        else:
            st.caption("詳細スコアはありません。")

    # クリアボタン
    if st.button("結果をクリアしてやり直す", use_container_width=True):
        for k in ("analysis",):
            st.session_state.pop(k, None)
        st.rerun()  # experimental_rerun の代わりにこちらを使用

