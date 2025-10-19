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
    {"title": "フレーミング効果", "body": "同じ内容でも“表現の仕方”によって印象が変わる心理。ポジティブな言い方だと良く見え、ネガティブだと悪く見える。例：『90％成功』vs『10％失敗』。"},
    {"title": "アンカリング効果", "body": "最初に見た数字や情報が“心の基準”となり、その後の判断を左右する。例：『定価10万円→7万円』と聞くと、本当は7万円が妥当でもお得に感じる。"},
    {"title": "現状維持バイアス", "body": "人は変化よりも“今のまま”を選びがち。変えることにエネルギーを使うより、維持する方が安心に感じる。例：古い習慣や職場に留まり続ける。"},
    {"title": "確証バイアス", "body": "自分の信じたい情報ばかり集め、反対意見を無視してしまう傾向。例：ダイエット方法を探す時に、自分に都合の良い情報ばかり信じる。"},
    {"title": "損失回避バイアス", "body": "人は“得する喜び”より“損する痛み”を強く感じる心理。例：500円得するより、500円失う方がショックが大きい。"},
    {"title": "代表性ヒューリスティック", "body": "見た目や印象が“典型的”だと感じるだけで、確率を誤る傾向。例：白衣を着た人を医者だと思い込む。"},
    {"title": "ハロー効果", "body": "一つの印象（見た目や肩書）が、全体評価に影響する心理。例：イケメンだから仕事もできると思い込む。"},
    {"title": "選択のパラドックス", "body": "選択肢が多すぎると満足度が下がる心理。例：レストランでメニューが多いと、選んだ後に“他の方が良かったかも”と感じる。"},
    {"title": "計画錯誤", "body": "自分の計画を“楽観的”に見積もる傾向。例：レポートを1日で終わると思っても、結局3日かかる。"},
    {"title": "社会的証明", "body": "多くの人がしている行動を“正しい”と感じる心理。例：行列があるお店を見て“人気だから美味しいに違いない”と思う。"},
    {"title": "プロスペクト理論", "body": "人は“確実な得”を選び、“確実な損”を避けようとする傾向。例：50％で1万円より、確実に5,000円を選ぶ。"},
    {"title": "サンクコスト効果", "body": "これまでの投資を無駄にしたくなくてやめられない心理。例：途中でつまらない映画でも“お金を払ったから”最後まで見る。"},
    {"title": "後知恵バイアス", "body": "結果を見た後に『そうなると思ってた』と感じる錯覚。例：株価が上がった後で“やっぱり買えばよかった”と思う。"},
    {"title": "自己奉仕バイアス", "body": "成功は自分の力、失敗は外部のせいにする傾向。例：試験に受かったら“努力の結果”、落ちたら“問題が悪い”。"},
    {"title": "時間割引", "body": "将来の利益より“今すぐの快楽”を優先する心理。例：将来の健康より、今のスイーツを選んでしまう。"},
    {"title": "楽観バイアス", "body": "自分は他人より失敗しにくいと思う錯覚。例：自分だけは事故に遭わないと信じて運転する。"},
    {"title": "権威バイアス", "body": "専門家や有名人の意見を過大評価する心理。例：有名人が紹介したサプリを根拠なく信じる。"},
    {"title": "同調バイアス", "body": "周囲の意見に合わせすぎて自分の考えを失う傾向。例：みんなが賛成している会議で反対意見を言えない。"},
    {"title": "利用可能性ヒューリスティック", "body": "思い出しやすい出来事を“頻繁”だと錯覚する。例：ニュースで事故を見た後、“交通事故は多い”と感じる。"},
    {"title": "感情ヒューリスティック", "body": "感情で判断してしまう傾向。例：不安で株を売る、嬉しくて衝動買いする。"},
    {"title": "ゴール・グラデーション効果", "body": "目標に近づくほどやる気が増す心理。例：スタンプカードがあと2個で満タンになると急に頑張る。"},
    {"title": "ナッジ効果", "body": "人の行動を“さりげなく誘導”する仕組み。例：健康食品を棚の目線の高さに置くと購入率が上がる。"},
    {"title": "リバウンド効果", "body": "節約やダイエットの制限が反動を生む現象。例：甘い物を我慢しすぎて、後でドカ食いする。"},
    {"title": "ゼイガルニク効果", "body": "“途中のこと”をよく覚えている心理。例：ドラマが中途半端で終わると次回が気になる。"},
    {"title": "投資家バイアス", "body": "自分の保有株を過大評価する心理。例：下がっても“そのうち上がる”と信じて売れない。"},
    {"title": "所有効果", "body": "自分の持ち物を実際より高く評価する心理。例：自分の古着は高く売れると思い込む。"},
    {"title": "アンビバレンス効果", "body": "好きと嫌いが同時に存在する心のゆらぎ。例：新しい環境にワクワクしつつ、不安も感じる。"},
    {"title": "確率の錯覚", "body": "小さな確率を過大評価する傾向。例：宝くじの当選を“自分にも起こりそう”と感じる。"},
    {"title": "選択的注意", "body": "自分が関心ある情報ばかり目に入り、他を見落とす。例：欲しい車の広告ばかり目につく。"},
    {"title": "ダニング＝クルーガー効果", "body": "知識が浅い人ほど自信過剰になる傾向。例：初心者が“もう完璧に理解した”と思い込む。"}
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

# === おまけ：今日の豆知識（1件だけ・ボタンは下） ===
with st.expander("おまけ：今日の豆知識", expanded=True):
    FACTS = [
        ("フレーミング効果", "同じ内容でも「90%成功」と言われると良く見え、「10%失敗」と言われると悪く見える。"),
        ("アンカリング", "最初に見た数字（定価など）が頭に残り、後の判断に影響する。"),
        ("現状維持バイアス", "今のままを選びやすい。変えるのが悪いわけじゃない。準備が大事。"),
        # …あなたが追加した20件もこの配列に入れておいてください…
    ]

    idx_key = k("fact_idx") if 'k' in globals() else "fact_idx"

    # 初期化（未設定なら 0）
    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0

    # 表示（← 先に出す：ボタンは後）
    i = st.session_state[idx_key] % len(FACTS)
    title, desc = FACTS[i]
    st.markdown(f"**{title}**：{desc}")

    # 次へボタン（on_click でインデックス更新 → 再実行後に上の表示が入れ替わる）
    def _next_fact():
        st.session_state[idx_key] = (st.session_state[idx_key] + 1) % len(FACTS)

    st.button("別の豆知識も見る", key=k("fact_next") if 'k' in globals() else "fact_next",
              on_click=_next_fact)



