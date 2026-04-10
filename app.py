import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Motorola Sales Dashboard",
    page_icon="📱",
    layout="wide"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px 20px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .metric-label { font-size: 13px; color: #888; margin-bottom: 4px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1a1a2e; }
    .chart-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .logo-bar {
        background: white;
        border-radius: 10px;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ─── DUMMY DATA ─────────────────────────────────────────────────────────────────
np.random.seed(42)

months = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

cities = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad",
          "Kolkata","Pune","Ahmedabad","Jaipur","Lucknow"]

city_coords = {
    "Mumbai":     (19.076, 72.877),
    "Delhi":      (28.613, 77.209),
    "Bangalore":  (12.972, 77.594),
    "Chennai":    (13.083, 80.270),
    "Hyderabad":  (17.385, 78.487),
    "Kolkata":    (22.573, 88.364),
    "Pune":       (18.520, 73.857),
    "Ahmedabad":  (23.023, 72.572),
    "Jaipur":     (26.912, 75.787),
    "Lucknow":    (26.850, 80.949),
}

models = ["iPhone SE", "OnePlus Nord", "Galaxy Note 20", "Moto G60", "Moto Edge 30"]
payment_methods = ["UPI", "Debit Card", "Cash", "Credit Card"]
day_names = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

# Generate transactions
n = 4000
df = pd.DataFrame({
    "month":          np.random.choice(months, n),
    "city":           np.random.choice(cities, n),
    "model":          np.random.choice(models, n),
    "payment_method": np.random.choice(payment_methods, n, p=[0.37,0.26,0.21,0.16]),
    "sales":          np.random.randint(5000, 80000, n),
    "quantity":       np.random.randint(1, 5, n),
    "rating":         np.random.choice([5,4,3,2,1], n, p=[0.40,0.30,0.15,0.10,0.05]),
    "day":            np.random.randint(1, 31, n),
    "day_name":       np.random.choice(day_names, n),
})

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗓️ Filter by Month")
    selected_months = []
    for m in months:
        if st.checkbox(m, value=True):
            selected_months.append(m)

if not selected_months:
    selected_months = months

filtered = df[df["month"].isin(selected_months)]

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 📱 Motorola Sales Dashboard")
st.markdown("---")

# ─── KPI METRICS ───────────────────────────────────────────────────────────────
total_sales    = filtered["sales"].sum()
total_qty      = filtered["quantity"].sum()
total_trans    = len(filtered)
avg_sale       = int(filtered["sales"].mean())

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">💰 Total Sales</div>
        <div class="metric-value">₹{total_sales/1e6:.1f}M</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">📦 Total Quantity</div>
        <div class="metric-value">{total_qty/1000:.0f}K</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">🔄 Transactions</div>
        <div class="metric-value">{total_trans/1000:.1f}K</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">📊 Avg Sale Value</div>
        <div class="metric-value">₹{avg_sale/1000:.0f}K</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── ROW 1: MAP + LINE CHART ───────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("#### 🗺️ Total Sales by City")
    city_sales = filtered.groupby("city")["sales"].sum().reset_index()
    city_sales["lat"] = city_sales["city"].map(lambda c: city_coords[c][0])
    city_sales["lon"] = city_sales["city"].map(lambda c: city_coords[c][1])

    fig_map = px.scatter_mapbox(
        city_sales, lat="lat", lon="lon",
        size="sales", color="sales",
        hover_name="city",
        hover_data={"sales": True, "lat": False, "lon": False},
        color_continuous_scale="Blues",
        size_max=40, zoom=3.8,
        mapbox_style="carto-positron",
        height=350
    )
    fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.markdown("#### 📈 Total Quantity by Day")
    qty_day = filtered.groupby("day")["quantity"].sum().reset_index()
    qty_day = qty_day.sort_values("day")

    fig_line = px.line(
        qty_day, x="day", y="quantity",
        markers=True,
        color_discrete_sequence=["#1f77b4"],
        height=350
    )
    fig_line.update_layout(
        xaxis_title="Day", yaxis_title="Quantity",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10,r=10,t=10,b=10)
    )
    fig_line.update_traces(line=dict(width=2), marker=dict(size=5))
    st.plotly_chart(fig_line, use_container_width=True)

# ─── ROW 2: BAR + PIE + FUNNEL + BAR ──────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### 📱 Sales by Mobile Model")
    model_sales = filtered.groupby("model")["sales"].sum().reset_index().sort_values("sales")
    fig_bar = px.bar(
        model_sales, x="sales", y="model",
        orientation="h",
        color_discrete_sequence=["#4472C4"],
        height=300
    )
    fig_bar.update_layout(
        xaxis_title="Sales", yaxis_title="",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=5,r=5,t=5,b=5)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("#### 💳 Payment Method")
    pay = filtered.groupby("payment_method")["sales"].count().reset_index()
    pay.columns = ["method", "count"]
    fig_pie = px.pie(
        pay, names="method", values="count",
        color_discrete_sequence=["#E74C3C","#3498DB","#2ECC71","#9B59B6"],
        height=300
    )
    fig_pie.update_layout(margin=dict(l=5,r=5,t=5,b=5))
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with col3:
    st.markdown("#### ⭐ Customer Ratings")
    rating_map = {5:"★★★★★",4:"★★★★☆",3:"★★★☆☆",2:"★★☆☆☆",1:"★☆☆☆☆"}
    rat = filtered.groupby("rating").size().reset_index(name="count")
    rat["label"] = rat["rating"].map(rating_map)
    rat = rat.sort_values("rating", ascending=False)

    fig_funnel = go.Figure(go.Funnel(
        y=rat["label"], x=rat["count"],
        marker=dict(color=["#2ECC71","#27AE60","#F39C12","#E67E22","#E74C3C"]),
        textinfo="value+percent total"
    ))
    fig_funnel.update_layout(
        height=300, margin=dict(l=5,r=5,t=5,b=5),
        paper_bgcolor="white"
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col4:
    st.markdown("#### 📅 Sales by Day Name")
    day_order = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    day_sales = filtered.groupby("day_name")["sales"].sum().reset_index()
    day_sales["day_name"] = pd.Categorical(day_sales["day_name"], categories=day_order, ordered=True)
    day_sales = day_sales.sort_values("day_name")

    fig_day = px.bar(
        day_sales, x="day_name", y="sales",
        color_discrete_sequence=["#1ABC9C"],
        height=300
    )
    fig_day.update_layout(
        xaxis_title="", yaxis_title="Sales",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=5,r=5,t=5,b=5)
    )
    st.plotly_chart(fig_day, use_container_width=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📊 Motorola Sales Dashboard | Built with Streamlit & Plotly | Dummy Data")