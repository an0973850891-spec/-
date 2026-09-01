import streamlit as st

# 設定網頁標題與手機最佳化配置
st.set_page_config(
    page_title="手機版台股損益計算機",
    page_icon="📱",
    layout="centered"
)

st.title("📱 台股損益精算機")
st.write("精算含手續費與證交稅的實際損益")

# 手機直式輸入區
with st.container():
    buy_price = st.number_input("📌 買進單價 (元)", value=34.14, step=0.01, format="%.2f")
    shares = st.number_input("📌 持有 / 買進股數", value=1500, step=100)
    sell_price = st.number_input("📌 預計賣出單價 (元)", value=35.00, step=0.01, format="%.2f")
    
    # 費率設定
    fee_rate = 0.001425  # 台股手續費率 0.1425%
    tax_rate = 0.003     # 證交稅 0.3%

# 點擊按鈕才計算
calculate_btn = st.button("計算完整結果", type="primary", use_container_width=True)

if calculate_btn:
    # 1. 買進金額與手續費
    buy_amount = buy_price * shares
    buy_fee = buy_amount * fee_rate
    
    # 2. 賣出金額、手續費、證交稅
    sell_amount = sell_price * shares
    sell_fee = sell_amount * fee_rate
    sell_tax = sell_amount * tax_rate
    
    # 3. 投資成本 (買進金額 + 買入手續費)
    total_investment = buy_amount + buy_fee
    
    # 4. 實得金額 (賣出金額 - 賣出手續費 - 證交稅)
    net_sell_amount = sell_amount - sell_fee - sell_tax
    
    # 5. 實質損益金額與報酬率
    profit = net_sell_amount - total_investment
    roi = (profit / total_investment) * 100 if total_investment > 0 else 0

    st.markdown("---")
    st.subheader("📊 詳細試算明細")

    # 數據展示卡片
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="投資成本 (含手續費)", value=f"${total_investment:,.2f}")
        st.metric(label="賣出價格", value=f"${sell_price:,.2f}")
        st.metric(label="買入手續費", value=f"${buy_fee:,.2f}")
    with col2:
        st.metric(label="賣出總額", value=f"${sell_amount:,.2f}")
        st.metric(label="賣出手續費", value=f"${sell_fee:,.2f}")
        st.metric(label="證券交易稅", value=f"${sell_tax:,.2f}")

    st.markdown("---")

    if profit >= 0:
        st.success(f"✨ 實質損益金額：+ $ {profit:,.2f} \n\n📈 實際報酬率：+{roi:.2f}%")
    else:
        st.error(f"⚠️ 實質損益金額：$ {profit:,.2f} \n\n📉 實際報酬率：{roi:.2f}%")
