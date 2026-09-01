import streamlit as st

# 設定網頁標題與手機最佳化配置
st.set_page_config(
    page_title="手機版股票損益計算機",
    page_icon="📱",
    layout="centered"
)

st.title("📱 股票損益計算機")
st.write("請輸入數值後，點擊按鈕查看計算結果")

# 手機直式輸入區
with st.container():
    buy_price = st.number_input("📌 買進單價 (元)", value=34.14, step=0.01, format="%.2f")
    shares = st.number_input("📌 持有 / 買進股數", value=1500, step=100)
    sell_price = st.number_input("📌 預計賣出單價 (元)", value=35.00, step=0.01, format="%.2f")

# 新增一個明顯的「計算結果」按鈕（手機版滿版點擊更方便）
calculate_btn = st.button("計算結果", type="primary", use_container_width=True)

# 當按鈕被點擊時，才執行計算與顯示結果
if calculate_btn:
    total_cost = buy_price * shares
    total_sell = sell_price * shares
    profit = total_sell - total_cost
    roi = (profit / total_cost) * 100 if total_cost > 0 else 0

    st.markdown("---")
    st.subheader("📊 試算結果")

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
