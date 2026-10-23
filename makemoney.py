import streamlit as st
import pandas as pd
import numpy as np

# 手機最佳化配置
st.set_page_config(
    page_title="元大台股損益試算表",
    page_icon="📊",
    layout="centered"
)

st.title("📊 元大台股智慧損益試算表")

# 交易參數設定區
with st.container():
    st.subheader("⚙️ 交易參數 (元大電子單)")
    
    # 按鈕切換交易方向
    direction = st.radio(
        "選擇交易方向", 
        ["📈 作多 (Long)", "📉 作空 (Short)"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
    
    trade_type = st.selectbox("交易類別", ["股票現股", "股票當沖"])
    
    price_label = "買入價格 (元)" if "作多" in direction else "放空價格 (元)"
    base_price = st.number_input(price_label, value=118.5, step=0.1, format="%.2f")
    shares = st.number_input("交易股數", value=1000, step=100)

# 元大證券費率設定 (電子單 6 折，整股低消 20 元、零股低消 1 元)
# 若股數 < 1000 視為零股，套用 1 元低消；整股則套用 20 元低消
def calc_fee(amount, is_odd_lot):
    raw_fee = amount * 0.001425 * 0.6  # 6折
    min_fee = 1 if is_odd_lot else 20
    return max(min_fee, round(raw_fee))

is_odd_lot = shares < 1000
tax_rate = 0.0015 if trade_type == "股票當沖" else 0.003

# 計算損益兩平價與基準數據
break_even_price = base_price
step_size = 0.5 if base_price >= 100 else 0.1
is_long = "作多" in direction

if is_long:
    buy_amount = base_price * shares
    buy_fee = calc_fee(buy_amount, is_odd_lot)
    total_investment = buy_amount + buy_fee
    
    # 尋找作多的損益兩平價
    for p in np.arange(base_price - 10, base_price + 10, 0.001):
        sa = p * shares
        sf = calc_fee(sa, is_odd_lot)
        stax = round(sa * tax_rate)
        net_sell = sa - sf - stax
        if net_sell >= total_investment:
            break_even_price = round(p, 2)
            break
            
else:  # 作空
    initial_sell_amount = base_price * shares
    initial_sell_fee = calc_fee(initial_sell_amount, is_odd_lot)
    initial_tax = round(initial_sell_amount * tax_rate)
    short_revenue = initial_sell_amount - initial_sell_fee - initial_tax
    
    # 尋找作空的損益兩平價
    for p in np.arange(base_price + 10, base_price - 10, -0.001):
        buy_back_amount = p * shares
        buy_back_fee = calc_fee(buy_back_amount, is_odd_lot)
        total_cover_cost = buy_back_amount + buy_back_fee
        if short_revenue >= total_cover_cost:
            break_even_price = round(p, 2)
            break

# 頂部摘要
st.markdown("---")
st.subheader("📌 試算摘要")
col1, col2 = st.columns(2)
col1.metric("進場價格", f"{base_price} 元")
col2.metric("損益兩平價 (中心點)", f"{break_even_price} 元")

# 矩陣表格
st.markdown("---")
direction_text = "作多（股價高於兩平價獲利）" if is_long else "作空（股價低於兩平價獲利）"
st.write(f"📈 **以損益兩平點為中心（上下各 10 檔）— {direction_text}**：")

prices = np.round(np.arange(break_even_price - (step_size * 10), break_even_price + (step_size * 10.1), step_size), 2)

table_data = []
for p in prices:
    if is_long:
        sell_amount = p * shares
        sell_fee = calc_fee(sell_amount, is_odd_lot)
        sell_tax = round(sell_amount * tax_rate)
        net_sell = sell_amount - sell_fee - sell_tax
        profit = net_sell - total_investment
        roi = (profit / total_investment) * 100
        cost_display = int(round(total_investment))
        fee_buy = buy_fee
        fee_sell = sell_fee
        tax_val = sell_tax
        price_col_name = "賣出價格"
    else:
        buy_back_amount = p * shares
        buy_back_fee = calc_fee(buy_back_amount, is_odd_lot)
        total_cover_cost = buy_back_amount + buy_back_fee
        profit = short_revenue - total_cover_cost
        roi = (profit / short_revenue) * 100 if short_revenue > 0 else 0
        cost_display = int(round(short_revenue))
        fee_buy = initial_sell_fee
        fee_sell = buy_back_fee
        tax_val = initial_tax
        price_col_name = "買回價格"

    table_data.append({
        price_col_name: f"{p:.2f}",
        "損益金額": int(round(profit)),
        "報酬率": f"{roi:.1f}%",
        "進場手續費": fee_buy,
        "出場手續費": fee_sell,
        "證交稅": tax_val,
        "交易基數": cost_display
    })

df_result = pd.DataFrame(table_data)

# 設定表格樣式：自動高亮損益兩平價那一列
def style_table(row):
    try:
        col_name = "賣出價格" if is_long else "買回價格"
        if abs(float(row[col_name]) - break_even_price) < (step_size / 2):
            return ['background-color: #fff3cd'] * len(row)
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
