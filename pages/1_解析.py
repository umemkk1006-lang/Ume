# -*- coding: utf-8 -*-
# pages/2_バイアス解析.py
import streamlit as st
import random
import datetime
from logic_simple import analyze_selection, render_finding_card

 
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

# =================
# 解析ボタン
# =================
if st.button("解析する", type="primary", key=k("analyze_btn")):
    # 簡単解析ロジックを呼ぶ
    findings = analyze_selection(theme, situation, sign, user_text)

    # 結果をセッションに保存（None防止）
    st.session_state[k("findings")] = findings or []

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
# 友だちに話したくなる小ネタ（1つだけ表示）
# =========================


# 日替わりで変わるようにシード設定（同じ日は固定）
random.seed(datetime.date.today().isoformat())

TIPS = [
    # === 既存3件 ===
    {"title": "フレーミング効果", "body": "同じ内容でも「90%成功」と言われると良く見え、「10%失敗」と言われると悪く見える。"},
    {"title": "アンカリング", "body": "最初に見た数字（定価など）が頭に残り、後の判断に影響する。"},
    {"title": "現状維持バイアス", "body": "今のままを選びやすい。変えるのが悪いわけじゃない。準備が大事。"},

    # === 新規20件 ===
    {"title": "確証バイアス", "body": "自分の意見を裏づける情報ばかり集めてしまう。反対意見を1回読むだけでも判断精度が上がる。"},
    {"title": "損失回避バイアス", "body": "人は得をする喜びより、損をする痛みを2倍強く感じる。"},
    {"title": "代表性ヒューリスティック", "body": "“らしい”特徴を見ると確率を無視しがち。見た目と確率は別もの。"},
    {"title": "ハロー効果", "body": "1つの印象（見た目や肩書）が全体評価に影響する。中身を個別に見る習慣を。"},
    {"title": "選択のパラドックス", "body": "選択肢が多いと自由なのに決めにくく、満足度も下がる。"},
    {"title": "計画錯誤", "body": "自分の予定を楽観的に見積もる傾向。過去の平均時間を基準に。"},
    {"title": "社会的証明", "body": "“みんながやっている”と安心する心理。多数派が正しいとは限らない。"},
    {"title": "現状バイアス", "body": "変える労力を避けることで、長期的損失を見逃すことも。"},
    {"title": "プロスペクト理論", "body": "人は利益より損失を強く意識し、確実な利益を優先しがち。"},
    {"title": "サンクコスト効果", "body": "すでに使ったお金や時間を惜しんで非合理な決断をすること。"},
    {"title": "後知恵バイアス", "body": "結果を知ると『最初から分かってた』と思ってしまう。"},
    {"title": "自己奉仕バイアス", "body": "成功は自分のおかげ、失敗は外部要因のせいにしがち。"},
    {"title": "時間割引", "body": "将来より“今”の利益を重く見てしまう。貯金が難しい理由のひとつ。"},
    {"title": "楽観バイアス", "body": "自分だけは大丈夫だと思ってしまう傾向。リスクも客観的に。"},
    {"title": "権威バイアス", "body": "専門家や上位者の意見を過大評価してしまう。根拠を一度確認。"},
    {"title": "同調圧力", "body": "周囲に合わせることで安心感を得るが、自分の目的を見失いやすい。"},
    {"title": "利用可能性ヒューリスティック", "body": "思い出しやすい出来事を“頻繁”だと錯覚する。"},
    {"title": "感情ヒューリスティック", "body": "感情が判断を支配する。強い感情のときは一晩おく。"},
    {"title": "ゴール・グラデーション効果", "body": "目標が近づくほどモチベーションが上がる。進捗を可視化すると続けやすい。"},
    {"title": "ナッジ効果", "body": "選択肢の“見せ方”次第で、人の行動は変わる。環境設計も立派な工夫。"},
    {"title": "リバウンド効果", "body": "節約や我慢のあとに反動で浪費してしまう。小さなご褒美を定期的に。"},
    {"title": "ゼイガルニク効果", "body": "途中で止まった作業は気になり続ける。逆に小さく始めると続きやすい。"},
]

# セッションに「すでに見たネタ」を記録して重複を減らす
if "tips_seen" not in st.session_state:
    st.session_state["tips_seen"] = set()

remaining = [i for i in range(len(TIPS)) if i not in st.session_state["tips_seen"]]
if not remaining:
    # すべて出し切ったらリセットして再びシャッフル
    st.session_state["tips_seen"].clear()
    remaining = list(range(len(TIPS)))

idx = random.choice(remaining)
st.session_state["tips_seen"].add(idx)
tip = TIPS[idx]

with st.expander("おまけ：今日の豆知識", expanded=False):
    st.markdown(f"**{tip['title']}**：{tip['body']}")
    if st.button("別の豆知識も見る", key="more_tip_btn"):
        remaining2 = [i for i in range(len(TIPS)) if i not in st.session_state["tips_seen"]]
        if not remaining2:
            st.session_state["tips_seen"].clear()
            remaining2 = list(range(len(TIPS)))
        idx2 = random.choice(remaining2)
        st.session_state["tips_seen"].add(idx2)
        tip2 = TIPS[idx2]
        st.markdown(f"**{tip2['title']}**：{tip2['body']}")
