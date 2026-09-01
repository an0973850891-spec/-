import streamlit as st
import pandas as pd
import numpy as np

# 設定網頁標題與手機最佳化配置
st.set_page_config(
    page_title="台股損益試算矩陣",
    page_icon="📊",
    layout="wide"  # 寬版面適合展示表格
)

st.title("📊 台股智慧損益試算表")

# 左側：交易參數設定區
st.sidebar.header("⚙️ 交易參數設定")

trade_type = st.sidebar.selectbox("交易類別", ["股票現股", "股票當沖"])
buy_price = st.sidebar.number_input("買入價格 (元)", value=118.5, step=0.1, format="%.2f")
sell_price_input = st.sidebar.number_input("預設賣出價格 (元)", value=119.5, step=0.1, format="%.2f")
shares = st.sidebar.number_input("交易股數", value=1000, step=100)

# 費率設定 (台股預設值)
fee_rate = 0.001425  # 手續費率 0.1425%
# 當沖證交稅減半為 0.15%，一般現股為 0.3%
tax_rate = 0.0015 if trade_type == "股票當沖" else 0.003

# 右側：試算結果與矩陣表格
st.subheader("📌 試算結果")

# 計算基準點數據
buy_amount = buy_price * shares
buy_fee = round(buy_amount * fee_rate)
total_investment = buy_amount + buy_fee

# 尋找損益兩平點賣出價 (即淨賣出金額剛好等於投資成本)
# 迴圈反推損益兩平價
break_even_price = buy_price
for p in np.arange(buy_price - 5, buy_price + 5, 0.01):
    sa = p * shares
    sf = round(sa * fee_rate)
    stax = round(sa * tax_rate)
    if (sa - sf - stax) >= total_investment:
        break_even_price = round(p, 2)
        break

# 頂部小標籤顯示
col_info1, col_info2, col_info3 = st.columns(3)
col_info1.metric("買入價格", f"{buy_price} 元")
col_info2.metric("預設賣出價格", f"{sell_price_input} 元")
col_info3.metric("損益兩平價格", f"{break_even_price} 元")

st.markdown("---")
st.write("📈 **不同賣出價格之損益模擬矩陣**（自動列出預設賣出價上下起伏的明細）：")

# 產生以預設賣出價為中心、上下各 5 個跳動檔位的表格
# 根據股價決定跳動單位 (例如 100元以上通常跳0.5元，或自訂步幅)
step_size = 0.5 if buy_price >= 100 else 0.1
prices = np.round(np.arange(sell_price_input - (step_size * 4), sell_price_input + (step_size * 5), step_size), 2)

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
        "證券交易稅": sell_tax,
        "投資成本": int(round(total_investment))
    })

df_result = pd.DataFrame(table_data)

# 使用 pandas 樣式將目前選定的賣出價格那一列突顯（標記顏色）
def highlight_row(row):
    # 當賣出價格符合輸入的預設賣出價時高亮
    if float(row["賣出價格"]) == float(sell_price_input):
        return ['background-color: #fff3cd'] * len(row)
    return [''] * len(row)

st.dataframe(df_result.style.apply(highlight_row, axis=1), use_container_width=True)
