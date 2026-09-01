import streamlit as st
import pandas as pd
import numpy as np

# 手機最佳化配置（改回置中單欄，手機上下滑動最順暢）
st.set_page_config(
    page_title="台股損益試算表",
    page_icon="📊",
    layout="centered"
)

st.title("📊 台股智慧損益試算表")

# 交易參數設定區（直接放在主畫面，手機不用點側邊欄）
with st.container():
    st.subheader("⚙️ 交易參數")
    trade_type = st.selectbox("交易類別", ["股票現股", "股票當沖"])
    buy_price = st.number_input("買入價格 (元)", value=118.5, step=0.1, format="%.2f")
    sell_price_input = st.number_input("預設賣出價格 (元)", value=119.5, step=0.1, format="%.2f")
    shares = st.number_input("交易股數", value=1000, step=100)

# 費率設定
fee_rate = 0.001425
tax_rate = 0.0015 if trade_type == "股票當沖" else 0.003

# 計算基準點數據
buy_amount = buy_price * shares
buy_fee = round(buy_amount * fee_rate)
total_investment = buy_amount + buy_fee

# 計算損益兩平價
break_even_price = buy_price
for p in np.arange(buy_price - 5, buy_price + 5, 0.01):
    sa = p * shares
    sf = round(sa * fee_rate)
    stax = round(sa * tax_rate)
    if (sa - sf - stax) >= total_investment:
        break_even_price = round(p, 2)
        break

# 頂部摘要
st.markdown("---")
st.subheader("📌 試算摘要")
col1, col2 = st.columns(2)
col1.metric("買入價格", f"{buy_price} 元")
col2.metric("損益兩平價", f"{break_even_price} 元")

# 矩陣表格
st.markdown("---")
st.write("📈 **不同賣出價格之損益矩陣**：")

step_size = 0.5 if buy_price >= 100 else 0.1
prices = np.round(np.arange(sell_price_input - (step_size * 3), sell_price_input + (step_size * 4), step_size), 2)

table_data = []
for p in prices:
    sell_amount = p * shares
    sell_fee = round(sell_amount * fee_rate)
    sell_tax = round(sell_amount * tax_rate)
    net_sell = sell_amount - sell_fee - sell_tax
    profit = net_sell - total_investment
    roi = (profit / total_investment) * 100
    
    table_data.append({
        "賣出價格": f"{p:.2f}",
        "損益金額": int(round(profit)),
        "報酬率": f"{roi:.1f}%",
        "買入手續費": buy_fee,
        "賣出手續費": sell_fee,
        "證交稅": sell_tax,
        "投資成本": int(round(total_investment))
    })

df_result = pd.DataFrame(table_data)

def highlight_row(row):
    if float(row["賣出價格"]) == float(sell_price_input):
        return ['background-color: #fff3cd'] * len(row)
    return [''] * len(row)

st.dataframe(df_result.style.apply(highlight_row, axis=1), use_container_width=True)
