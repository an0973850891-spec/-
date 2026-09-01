import streamlit as st

# 設定網頁標題與手機最佳化配置（維持單欄置中，手機瀏覽最舒適）
st.set_page_config(
    page_title="手機版股票損益計算機",
    page_icon="📱",
    layout="centered"
)

st.title("📱 股票損益計算機")
st.write("適合手機快速輸入與查看的簡易計算工具")

# 手機直式輸入區（區塊分明，方便手指點擊）
with st.container():
    buy_price = st.number_input("📌 買進單價 (元)", value=34.14, step=0.01, format="%.2f")
    shares = st.number_input("📌 持有 / 買進股數", value=1500, step=100)
    sell_price = st.number_input("📌 預計賣出單價 (元)", value=35.00, step=0.01, format="%.2f")

# 計算邏輯
total_cost = buy_price * shares
total_sell = sell_price * shares
profit = total_sell - total_cost
roi = (profit / total_cost) * 100 if total_cost > 0 else 0

# 顯示結果區
st.markdown("---")
st.subheader("📊 試算結果")

# 使用手機好讀的大卡片格式
col1, col2 = st.columns(2)
with col1:
    st.metric(label="總投入成本", value=f"${total_cost:,.0f}")
with col2:
    st.metric(label="預計賣出總額", value=f"${total_sell:,.0f}")

st.markdown("---")

if profit >= 0:
    st.success(f"✨ 預估獲利：+ $ {profit:,.2f} （報酬率：+{roi:.2f}%）")
else:
    st.error(f"⚠️ 預估虧損：$ {profit:,.2f} （報酬率：{roi:.2f}%）")
