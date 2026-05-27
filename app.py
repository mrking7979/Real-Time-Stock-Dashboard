import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import numpy as np

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Smart Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

.stMetric {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #1F2937;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================
st.title("📈 Smart Real-Time Stock Dashboard")

st.markdown("""
Track live stock market data, technical indicators,
AI signals, and professional charts in real-time.
""")

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.header("⚙ Dashboard Settings")

# STOCK OPTIONS
stock_data = {
    "Apple Inc. (AAPL)": "AAPL",
    "Microsoft Corp. (MSFT)": "MSFT",
    "Tesla Inc. (TSLA)": "TSLA",
    "Amazon.com Inc. (AMZN)": "AMZN",
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Meta Platforms (META)": "META",
    "Netflix Inc. (NFLX)": "NFLX",
    "Alphabet Inc. (GOOGL)": "GOOGL"
}

selected_company = st.sidebar.selectbox(
    "📈 Select Company",
    list(stock_data.keys())
)

stock_symbol = stock_data[selected_company]

# TIME PERIOD
time_period = st.sidebar.selectbox(
    "📅 Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "5y"],
    index=2
)

# SHOW MOVING AVERAGE
show_ma = st.sidebar.checkbox(
    "Show Moving Average",
    value=True
)

# INVESTMENT INPUT
investment = st.sidebar.number_input(
    "💰 Investment Amount ($)",
    min_value=100,
    value=1000
)

# ==========================================
# FETCH STOCK DATA
# ==========================================
try:

    data = yf.download(
        stock_symbol,
        period=time_period,
        auto_adjust=True,
        progress=False
    )

    # FIX MULTI-INDEX ISSUE
    data.columns = [
        col[0] if isinstance(col, tuple) else col
        for col in data.columns
    ]

    # VALIDATION
    if data.empty:
        st.error("No stock data found.")

    else:

        # ==========================================
        # PRICE DATA
        # ==========================================
        close_prices = data["Close"]

        current_price = float(close_prices.iloc[-1])
        previous_price = float(close_prices.iloc[-2])

        price_change = current_price - previous_price

        percent_change = (
            price_change / previous_price
        ) * 100

        # ==========================================
        # MOVING AVERAGES
        # ==========================================
        data["MA5"] = close_prices.rolling(5).mean()
        data["MA20"] = close_prices.rolling(20).mean()

        # ==========================================
        # RSI CALCULATION
        # ==========================================
        delta = close_prices.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        latest_rsi = float(rsi.iloc[-1])

        # ==========================================
        # MARKET OVERVIEW
        # ==========================================
        st.subheader("📊 Market Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Current Price",
            f"${current_price:.2f}"
        )

        col2.metric(
            "Price Change",
            f"${price_change:.2f}"
        )

        col3.metric(
            "Percentage Change",
            f"{percent_change:.2f}%"
        )

        col4.metric(
            "RSI",
            f"{latest_rsi:.2f}"
        )

        # ==========================================
        # AI SIGNALS
        # ==========================================
        st.subheader("🤖 AI Trading Signals")

        if data["MA5"].iloc[-1] > data["MA20"].iloc[-1]:
            st.success(
                "📈 BUY SIGNAL: Bullish Momentum Detected"
            )
        else:
            st.error(
                "📉 SELL SIGNAL: Bearish Momentum Detected"
            )

        if latest_rsi > 70:
            st.warning(
                "⚠ RSI indicates stock may be OVERBOUGHT"
            )

        elif latest_rsi < 30:
            st.success(
                "✅ RSI indicates stock may be OVERSOLD"
            )

        else:
            st.info(
                "ℹ RSI indicates neutral market conditions"
            )

        # ==========================================
        # PORTFOLIO ESTIMATOR
        # ==========================================
        st.subheader("💰 Portfolio Estimator")

        shares = investment / current_price

        st.info(
            f"With ${investment:,.2f}, "
            f"you can buy approximately "
            f"{shares:.2f} shares of {stock_symbol}."
        )

        # ==========================================
        # ADVANCED STOCK CHART
        # ==========================================
        st.subheader("📈 Advanced Stock Chart")

        fig = go.Figure()

        # CANDLESTICK
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Candlestick"
            )
        )

        # MOVING AVERAGES
        if show_ma:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA5"],
                    mode="lines",
                    name="5-Day MA",
                    line=dict(
                        color="cyan",
                        width=2
                    )
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA20"],
                    mode="lines",
                    name="20-Day MA",
                    line=dict(
                        color="orange",
                        width=2
                    )
                )
            )

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_title="Date",
            yaxis_title="Stock Price",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==========================================
        # VOLUME CHART
        # ==========================================
        st.subheader("📊 Trading Volume")

        volume_fig = go.Figure()

        volume_fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                marker_color="lightgreen",
                name="Volume"
            )
        )

        volume_fig.update_layout(
            template="plotly_dark",
            height=400
        )

        st.plotly_chart(
            volume_fig,
            use_container_width=True
        )

        # ==========================================
        # RECENT STOCK DATA
        # ==========================================
        st.subheader("📄 Recent Stock Data")

        st.dataframe(
            data.tail(10),
            use_container_width=True
        )

        # ==========================================
        # DOWNLOAD BUTTON
        # ==========================================
        csv = data.to_csv().encode("utf-8")

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{stock_symbol}_data.csv",
            mime="text/csv"
        )

        # ==========================================
        # COMPANY INFORMATION
        # ==========================================
        st.subheader("🏢 Company Information")

        try:

            ticker = yf.Ticker(stock_symbol)

            info = ticker.info

            col5, col6 = st.columns(2)

            with col5:

                st.write("### Company Details")

                st.write(
                    "Company:",
                    info.get("longName", "N/A")
                )

                st.write(
                    "Sector:",
                    info.get("sector", "N/A")
                )

                st.write(
                    "Industry:",
                    info.get("industry", "N/A")
                )

            with col6:

                st.write("### Market Details")

                st.write(
                    "Country:",
                    info.get("country", "N/A")
                )

                st.write(
                    "Market Cap:",
                    info.get("marketCap", "N/A")
                )

                st.write(
                    "Website:",
                    info.get("website", "N/A")
                )

        except:
            st.warning(
                "Unable to fetch company information."
            )

        # ==========================================
        # STOCK NEWS
        # ==========================================
        st.subheader("📰 Latest Stock News")

        try:

            ticker = yf.Ticker(stock_symbol)

            news = ticker.news

            if news:

                for article in news[:5]:

                    title = article.get(
                        "title",
                        "No Title"
                    )

                    publisher = article.get(
                        "publisher",
                        "Unknown"
                    )

                    link = article.get(
                        "link",
                        ""
                    )

                    st.markdown(f"### {title}")

                    st.write(
                        f"Publisher: {publisher}"
                    )

                    st.markdown(
                        f"[Read Full Article]({link})"
                    )

                    st.markdown("---")

            else:
                st.warning("No news found.")

        except:
            st.warning(
                "Unable to fetch stock news."
            )

except Exception as e:

    st.error(f"Error: {e}")