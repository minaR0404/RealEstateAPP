import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "../data/realestate_sample.db"

# --------------------------------
# データ取得関数
# --------------------------------
def get_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM properties", conn)
    conn.close()
    return df

# --------------------------------
# Streamlit UI
# --------------------------------
st.set_page_config(page_title="不動産検索アプリ", layout="wide")
st.title("🏠 不動産データ検索アプリ")

# データ読み込み
try:
    df = get_data()
except Exception as e:
    st.error(f"データベースの読み込みに失敗しました: {e}")
    st.stop()

# 検索条件
st.sidebar.header("🔍 検索条件")
name_filter = st.sidebar.text_input("物件名で検索")
min_price = st.sidebar.number_input("最低価格", value=0, step=10000)
max_price = st.sidebar.number_input("最高価格", value=int(df["price"].max()), step=10000)

# フィルタリング処理
filtered_df = df[
    (df["price"] >= min_price) &
    (df["price"] <= max_price)
]

if name_filter:
    filtered_df = filtered_df[filtered_df["name"].str.contains(name_filter, case=False, na=False)]

# 結果表示
st.subheader("検索結果")
st.dataframe(filtered_df, use_container_width=True)

# 選択した物件の詳細
if not filtered_df.empty:
    selected_address = st.selectbox("都道府県を選択", filtered_df["address"].unique())
    selected_name = st.selectbox("詳細を見たい物件を選択", filtered_df[filtered_df.address==selected_address]["name"].unique())
    selected = filtered_df[filtered_df["name"] == selected_name].iloc[0]
    st.markdown("### 🏡 物件詳細")
    st.write(f"**物件名**： {selected['name']}")
    st.write(f"**住所**： {selected['address']}")
    st.write(f"**価格**： **{selected['price']:.0f} 円/m²**")
else:
    st.warning("条件に一致する物件がありません。")
