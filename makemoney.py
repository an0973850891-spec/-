import streamlit as st
import pandas as pd
import numpy as np

# 手機最佳化配置
st.set_page_config(
    page_title="台股損益試算表",
    page_icon="📊",
    layout="centered"
)

st.title("📊 台股智慧損益試算表")

# 交易參數設定區
with st.container():
    st.subheader("⚙️ 交易參數")
    trade_type = st.selectbox("交易類別", ["股票現股", "股票當沖"])
    buy_price = st.number_input("買入價格 (元)", value=118.5, step=0.1, format="%.2f")
    shares = st.number_input("交易股數", value=1000, step=100)

# 費率設定
fee_rate = 0.001425
tax_rate = 0.0015 if trade_type == "股票當沖" else 0.003

# 計算基準點數據
buy_amount = buy_price * shares
buy_fee = round(buy_amount * fee_rate)
total_investment = buy_amount + buy_fee

# 計算精準的損益兩平價 (報酬率為0的中心點)
break_even_price = buy_price
for p in np.arange(buy_price - 10, buy_price + 10, 0.001):
    sa = p * shares
    sf = round(sa * fee_rate)
    stax = round(sa * tax_rate)
    net_sell = sa - sf - stax
    if net_sell >= total_investment:
        break_even_price = round(p, 2)
        break

# 頂部摘要
st.markdown("---")
st.subheader("📌 試算摘要")
col1, col2 = st.columns(2)
col1.metric("買入價格", f"{buy_price} 元")
col2.metric("損益兩平價 (中心點)", f"{break_even_price} 元")

# 矩陣表格
st.markdown("---")
st.write("📈 **以損益兩平點為中心（上下各 10 檔）**：")

# 根據股價決定跳動單位 (100元以上通常跳0.5元，否則0.1元)
step_size = 0.5 if buy_price >= 100 else 0.1

# 以「損益兩平價」為中心，產生上方 10 檔與下方 10 檔（共 21 個價位）
prices = np.round(np.arange(break_even_price - (step_size * 10), break_even_price + (step_size * 10.1), step_size), 2)

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

# 設定表格樣式：自動高亮報酬率為 0（損益兩平價）的那一列
def style_table(row):
    try:
        if abs(float(row["賣出價格"]) - break_even_price) < (step_size / 2):
            return ['background-color: #fff3cd'] * len(row) # 黃色高亮中心點
    except:
        pass
    return [''] * len(row)

# 損益金額與報酬率紅綠字著色
def color_profit_loss(val):
    try:
        num = float(str(val).replace('%', ''))
        if num > 0:
            return 'color: #d9534f; font-weight: bold;'  # 紅色 (賺)
        elif num < 0:
            return 'color: #28a745; font-weight: bold;'  # 綠色 (賠)
    except:
        pass
    return ''

# 套用樣式
styled_df = df_result.style.apply(style_table, axis=1)
if hasattr(styled_df, 'map'):
    styled_df = styled_df.map(color_profit_loss, subset=["損益金額", "報酬率"])
else:
    styled_df = styled_df.applymap(color_profit_loss, subset=["損益金額", "報酬率"])

st.dataframe(styled_df, use_container_width=True)
