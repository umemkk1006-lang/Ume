# -*- coding: utf-8 -*-
# pages/2_バイアス解析.py

import streamlit as st

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
# 友だちに話したくなる小ネタ
# =========================
with st.expander("おまけ：今日の豆知識"):
    st.markdown("- **フレーミング効果**：同じ内容でも「90%成功」と言われると良く見え、「10%失敗」と言われると悪く見える。")
    st.markdown("- **アンカリング**：最初に見た数字（定価など）が頭に残り、後の判断に影響する。")
    st.markdown("- **現状維持バイアス**：今のままを選びやすい。変えるのが悪いわけじゃない。準備が大事。")


