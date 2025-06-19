"""
DISCLAIMER: 

This software is provided solely for educational and research purposes. 
It is not intended to provide investment advice, and no investment recommendations are made herein. 
The developers are not financial advisors and accept no responsibility for any financial decisions or losses resulting from the use of this software. 
Always consult a professional financial advisor before making any investment decisions.
"""

import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import time
from typing import Dict, Any, Optional, Tuple


# Configuration for API keys
API_KEYS = {
    'alpha_vantage': st.secrets.get("ALPHA_VANTAGE_API_KEY", "") if hasattr(st, 'secrets') else "",
    'polygon': st.secrets.get("POLYGON_API_KEY", "") if hasattr(st, 'secrets') else "",
    'iex': st.secrets.get("IEX_API_KEY", "") if hasattr(st, 'secrets') else "",
}


def filter_dates(dates):
    today = datetime.today().date()
    cutoff_date = today + timedelta(days=45)
    
    sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d").date() for date in dates)

    arr = []
    for i, date in enumerate(sorted_dates):
        if date >= cutoff_date:
            arr = [d.strftime("%Y-%m-%d") for d in sorted_dates[:i+1]]  
            break
    
    if len(arr) > 0:
        if arr[0] == today.strftime("%Y-%m-%d"):
            return arr[1:]
        return arr

    raise ValueError("No date 45 days or more in the future found.")


def yang_zhang(price_data, window=30, trading_periods=252, return_last_only=True):
    log_ho = (price_data['High'] / price_data['Open']).apply(np.log)
    log_lo = (price_data['Low'] / price_data['Open']).apply(np.log)
    log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
    
    log_oc = (price_data['Open'] / price_data['Close'].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2
    
    log_cc = (price_data['Close'] / price_data['Close'].shift(1)).apply(np.log)
    log_cc_sq = log_cc**2
    
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    
    close_vol = log_cc_sq.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    open_vol = log_oc_sq.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    window_rs = rs.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    k = 0.34 / (1.34 + ((window + 1) / (window - 1)) )
    result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(trading_periods)

    if return_last_only:
        return result.iloc[-1]
    else:
        return result.dropna()
    

def build_term_structure(days, ivs):
    days = np.array(days)
    ivs = np.array(ivs)

    sort_idx = days.argsort()
    days = days[sort_idx]
    ivs = ivs[sort_idx]

    spline = interp1d(days, ivs, kind='linear', fill_value="extrapolate")

    def term_spline(dte):
        if dte < days[0]:  
            return ivs[0]
        elif dte > days[-1]:
            return ivs[-1]
        else:  
            return float(spline(dte))

    return term_spline


def get_current_price_yfinance(ticker_symbol: str) -> Optional[float]:
    """Get current price using yfinance"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        todays_data = ticker.history(period='1d')
        if not todays_data.empty:
            return float(todays_data['Close'].iloc[-1])
    except Exception as e:
        st.warning(f"YFinance failed: {str(e)}")
    return None


def get_current_price_alpha_vantage(ticker_symbol: str) -> Optional[float]:
    """Get current price using Alpha Vantage"""
    if not API_KEYS['alpha_vantage']:
        return None
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker_symbol,
            'apikey': API_KEYS['alpha_vantage']
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            return float(data['Global Quote']['05. price'])
    except Exception as e:
        st.warning(f"Alpha Vantage failed: {str(e)}")
    return None


def get_current_price_polygon(ticker_symbol: str) -> Optional[float]:
    """Get current price using Polygon.io"""
    if not API_KEYS['polygon']:
        return None
    
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker_symbol}/prev"
        params = {'apikey': API_KEYS['polygon']}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            return float(data['results'][0]['c'])  # Close price
    except Exception as e:
        st.warning(f"Polygon.io failed: {str(e)}")
    return None


def get_current_price_iex(ticker_symbol: str) -> Optional[float]:
    """Get current price using IEX Cloud"""
    if not API_KEYS['iex']:
        return None
    
    try:
        url = f"https://cloud.iexapis.com/stable/stock/{ticker_symbol}/quote"
        params = {'token': API_KEYS['iex']}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'latestPrice' in data:
            return float(data['latestPrice'])
    except Exception as e:
        st.warning(f"IEX Cloud failed: {str(e)}")
    return None


def get_current_price_fallback(ticker_symbol: str) -> Tuple[Optional[float], str]:
    """Get current price with multiple data source fallbacks"""
    
    # Try yfinance first (most reliable for options data)
    price = get_current_price_yfinance(ticker_symbol)
    if price is not None:
        return price, "Yahoo Finance"
    
    st.warning("⚠️ Yahoo Finance rate limited. Trying alternative sources...")
    
    # Try Alpha Vantage
    price = get_current_price_alpha_vantage(ticker_symbol)
    if price is not None:
        return price, "Alpha Vantage"
    
    # Try Polygon.io
    price = get_current_price_polygon(ticker_symbol)
    if price is not None:
        return price, "Polygon.io"
    
    # Try IEX Cloud
    price = get_current_price_iex(ticker_symbol)
    if price is not None:
        return price, "IEX Cloud"
    
    return None, "None"


def get_price_history_alpha_vantage(ticker_symbol: str) -> Optional[pd.DataFrame]:
    """Get price history using Alpha Vantage"""
    if not API_KEYS['alpha_vantage']:
        return None
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker_symbol,
            'outputsize': 'compact',  # Last 100 days
            'apikey': API_KEYS['alpha_vantage']
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match yfinance format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            
            # Get last 3 months
            cutoff_date = datetime.now() - timedelta(days=90)
            df = df[df.index >= cutoff_date]
            
            return df
    except Exception as e:
        st.warning(f"Alpha Vantage history failed: {str(e)}")
    return None


def get_price_history_polygon(ticker_symbol: str) -> Optional[pd.DataFrame]:
    """Get price history using Polygon.io"""
    if not API_KEYS['polygon']:
        return None
    
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker_symbol}/range/1/day/{start_date}/{end_date}"
        params = {'apikey': API_KEYS['polygon']}
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            df_data = []
            for result in data['results']:
                df_data.append({
                    'Open': result['o'],
                    'High': result['h'],
                    'Low': result['l'],
                    'Close': result['c'],
                    'Volume': result['v']
                })
            
            df = pd.DataFrame(df_data)
            df.index = pd.to_datetime([datetime.fromtimestamp(r['t']/1000) for r in data['results']])
            return df
    except Exception as e:
        st.warning(f"Polygon.io history failed: {str(e)}")
    return None


def get_price_history_fallback(ticker_symbol: str) -> Tuple[Optional[pd.DataFrame], str]:
    """Get price history with multiple data source fallbacks"""
    
    # Try yfinance first
    try:
        stock = yf.Ticker(ticker_symbol)
        price_history = stock.history(period='3mo')
        if not price_history.empty:
            return price_history, "Yahoo Finance"
    except Exception as e:
        st.warning(f"YFinance history failed: {str(e)}")
    
    st.warning("⚠️ Yahoo Finance rate limited for price history. Trying alternatives...")
    
    # Try Alpha Vantage
    price_history = get_price_history_alpha_vantage(ticker_symbol)
    if price_history is not None and not price_history.empty:
        return price_history, "Alpha Vantage"
    
    # Try Polygon.io
    price_history = get_price_history_polygon(ticker_symbol)
    if price_history is not None and not price_history.empty:
        return price_history, "Polygon.io"
    
    return None, "None"


def create_mock_options_data(ticker_symbol: str, current_price: float) -> Dict[str, Any]:
    """Create mock options data when real options data is unavailable"""
    st.warning("⚠️ Options data unavailable. Using estimated values for demonstration.")
    
    # Generate mock expiration dates
    today = datetime.today().date()
    exp_dates = []
    for weeks in [1, 2, 4, 8, 12]:
        exp_date = today + timedelta(weeks=weeks)
        # Adjust to Friday
        exp_date = exp_date + timedelta(days=(4 - exp_date.weekday()) % 7)
        exp_dates.append(exp_date.strftime("%Y-%m-%d"))
    
    # Generate mock IV data (decreasing with time)
    base_iv = 0.3  # 30% base IV
    dtes = []
    ivs = []
    
    for i, exp_date in enumerate(exp_dates):
        exp_date_obj = datetime.strptime(exp_date, "%Y-%m-%d").date()
        days_to_expiry = (exp_date_obj - today).days
        dtes.append(days_to_expiry)
        # Higher IV for shorter dates
        iv = base_iv * (1 + 0.1 * (4 - i) / 4)
        ivs.append(iv)
    
    # Mock straddle price (estimated)
    estimated_straddle = current_price * 0.05  # 5% of stock price
    
    return {
        'dtes': dtes,
        'ivs': ivs,
        'straddle': estimated_straddle,
        'exp_dates': exp_dates
    }


@st.cache_data(ttl=300)  # Cache for 5 minutes
def compute_recommendation(ticker_symbol: str):
    try:
        ticker_symbol = ticker_symbol.strip().upper()
        if not ticker_symbol:
            return {"error": "No stock symbol provided."}
        
        # Get current price with fallbacks
        underlying_price, price_source = get_current_price_fallback(ticker_symbol)
        if underlying_price is None:
            return {"error": "Unable to retrieve current stock price from any source."}
        
        # Try to get options data (yfinance only for now)
        options_data = None
        options_available = False
        
        try:
            stock = yf.Ticker(ticker_symbol)
            if len(stock.options) > 0:
                exp_dates = list(stock.options)
                exp_dates = filter_dates(exp_dates)
                options_available = True
                
                options_chains = {}
                for exp_date in exp_dates:
                    options_chains[exp_date] = stock.option_chain(exp_date)
        except Exception as e:
            st.warning(f"Options data unavailable: {str(e)}")
            options_available = False
        
        # Get price history with fallbacks
        price_history, history_source = get_price_history_fallback(ticker_symbol)
        if price_history is None:
            return {"error": "Unable to retrieve price history from any source."}
        
        # Process options data or use mock data
        if options_available:
            atm_iv = {}
            straddle = None
            
            for i, (exp_date, chain) in enumerate(options_chains.items()):
                calls = chain.calls
                puts = chain.puts

                if calls.empty or puts.empty:
                    continue

                call_diffs = (calls['strike'] - underlying_price).abs()
                call_idx = call_diffs.idxmin()
                call_iv = calls.loc[call_idx, 'impliedVolatility']

                put_diffs = (puts['strike'] - underlying_price).abs()
                put_idx = put_diffs.idxmin()
                put_iv = puts.loc[put_idx, 'impliedVolatility']

                atm_iv_value = (call_iv + put_iv) / 2.0
                atm_iv[exp_date] = atm_iv_value

                if i == 0:
                    call_bid = calls.loc[call_idx, 'bid']
                    call_ask = calls.loc[call_idx, 'ask']
                    put_bid = puts.loc[put_idx, 'bid']
                    put_ask = puts.loc[put_idx, 'ask']
                    
                    if (call_bid is not None and call_ask is not None and 
                        put_bid is not None and put_ask is not None):
                        call_mid = (call_bid + call_ask) / 2.0
                        put_mid = (put_bid + put_ask) / 2.0
                        straddle = call_mid + put_mid
            
            if not atm_iv:
                # Fallback to mock data
                mock_data = create_mock_options_data(ticker_symbol, underlying_price)
                dtes = mock_data['dtes']
                ivs = mock_data['ivs']
                straddle = mock_data['straddle']
                data_source = "Estimated (Options unavailable)"
            else:
                # Process real options data
                today = datetime.today().date()
                dtes = []
                ivs = []
                for exp_date, iv in atm_iv.items():
                    exp_date_obj = datetime.strptime(exp_date, "%Y-%m-%d").date()
                    days_to_expiry = (exp_date_obj - today).days
                    dtes.append(days_to_expiry)
                    ivs.append(iv)
                data_source = "Real Options Data"
        else:
            # Use mock data
            mock_data = create_mock_options_data(ticker_symbol, underlying_price)
            dtes = mock_data['dtes']
            ivs = mock_data['ivs']
            straddle = mock_data['straddle']
            data_source = "Estimated (Options unavailable)"
        
        # Build term structure
        term_spline = build_term_structure(dtes, ivs)
        ts_slope_0_45 = (term_spline(45) - term_spline(dtes[0])) / (45 - dtes[0])
        
        # Calculate volatility metrics
        rv30 = yang_zhang(price_history)
        iv30_rv30 = term_spline(30) / rv30

        # Calculate volume metrics
        avg_volume = price_history['Volume'].rolling(30).mean().dropna().iloc[-1]
        expected_move = round(straddle / underlying_price * 100, 2) if straddle else None

        return {
            'success': True,
            'ticker': ticker_symbol,
            'underlying_price': underlying_price,
            'price_source': price_source,
            'history_source': history_source,
            'options_source': data_source,
            'avg_volume': avg_volume,
            'avg_volume_pass': avg_volume >= 1500000,
            'iv30_rv30': iv30_rv30,
            'iv30_rv30_pass': iv30_rv30 >= 1.25,
            'ts_slope_0_45': ts_slope_0_45,
            'ts_slope_pass': ts_slope_0_45 <= -0.00406,
            'expected_move': expected_move,
            'dtes': dtes,
            'ivs': ivs,
            'rv30': rv30,
            'price_history': price_history
        }
        
    except Exception as e:
        return {"error": f"Error occurred processing: {str(e)}"}


def create_iv_chart(dtes, ivs):
    """Create an interactive chart showing the implied volatility term structure"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dtes,
        y=ivs,
        mode='lines+markers',
        name='Implied Volatility',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Implied Volatility Term Structure",
        xaxis_title="Days to Expiration",
        yaxis_title="Implied Volatility",
        height=400,
        showlegend=True
    )
    
    return fig


def create_price_chart(price_history):
    """Create an interactive price chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=price_history.index,
        open=price_history['Open'],
        high=price_history['High'],
        low=price_history['Low'],
        close=price_history['Close'],
        name="Price"
    ))
    
    fig.update_layout(
        title="3-Month Price History",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=400,
        xaxis_rangeslider_visible=False
    )
    
    return fig


def main():
    st.set_page_config(
        page_title="Earnings Position Checker",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Earnings Position Checker")
    st.markdown("*Analyze stock options for earnings trading opportunities*")
    
    # Add disclaimer
    with st.expander("⚠️ Important Disclaimer"):
        st.warning("""
        This software is provided solely for educational and research purposes. 
        It is not intended to provide investment advice, and no investment recommendations are made herein. 
        The developers are not financial advisors and accept no responsibility for any financial decisions or losses resulting from the use of this software. 
        Always consult a professional financial advisor before making any investment decisions.
        """)
    
    # API Key Configuration
    with st.expander("🔑 API Key Configuration (Optional - for better reliability)"):
        st.markdown("""
        To avoid rate limiting, you can optionally provide API keys for alternative data sources:
        
        - **Alpha Vantage**: Get free API key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
        - **Polygon.io**: Get free API key at [polygon.io](https://polygon.io/)  
        - **IEX Cloud**: Get free API key at [iexcloud.io](https://iexcloud.io/)
        
        Add these to your Streamlit secrets or set as environment variables.
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Alpha Vantage API Key", type="password", help="Optional")
        with col2:
            st.text_input("Polygon.io API Key", type="password", help="Optional")
        with col3:
            st.text_input("IEX Cloud API Key", type="password", help="Optional")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Stock Symbol:",
            placeholder="e.g., AAPL, TSLA, MSFT",
            help="Enter a stock ticker symbol to analyze"
        ).upper()
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary")
    
    if analyze_button and ticker_input:
        with st.spinner(f"Analyzing {ticker_input}..."):
            result = compute_recommendation(ticker_input)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
            return
        
        # Display results
        st.success(f"✅ Analysis complete for {result['ticker']}")
        
        # Data source information
        with st.expander("ℹ️ Data Sources Used"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Current Price:** {result['price_source']}")
            with col2:
                st.info(f"**Price History:** {result['history_source']}")
            with col3:
                st.info(f"**Options Data:** {result['options_source']}")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${result['underlying_price']:.2f}"
            )
        
        with col2:
            st.metric(
                "Expected Move",
                f"{result['expected_move']:.2f}%" if result['expected_move'] else "N/A"
            )
        
        with col3:
            st.metric(
                "30-Day Avg Volume",
                f"{result['avg_volume']:,.0f}"
            )
        
        with col4:
            st.metric(
                "IV30/RV30 Ratio",
                f"{result['iv30_rv30']:.2f}"
            )
        
        # Recommendation logic
        avg_volume_pass = result['avg_volume_pass']
        iv30_rv30_pass = result['iv30_rv30_pass']
        ts_slope_pass = result['ts_slope_pass']
        
        if avg_volume_pass and iv30_rv30_pass and ts_slope_pass:
            recommendation = "RECOMMENDED"
            color = "success"
            icon = "✅"
        elif ts_slope_pass and ((avg_volume_pass and not iv30_rv30_pass) or (iv30_rv30_pass and not avg_volume_pass)):
            recommendation = "CONSIDER"
            color = "warning"
            icon = "⚠️"
        else:
            recommendation = "AVOID"
            color = "error"
            icon = "❌"
        
        # Display recommendation
        if color == "success":
            st.success(f"{icon} **{recommendation}** - All criteria met for earnings trade")
        elif color == "warning":
            st.warning(f"{icon} **{recommendation}** - Some criteria met, proceed with caution")
        else:
            st.error(f"{icon} **{recommendation}** - Criteria not met for earnings trade")
        
        # Detailed criteria
        st.subheader("📊 Detailed Analysis")
        
        criteria_data = {
            "Criteria": [
                "Average Volume ≥ 1.5M",
                "IV30/RV30 Ratio ≥ 1.25",
                "Term Structure Slope ≤ -0.00406"
            ],
            "Value": [
                f"{result['avg_volume']:,.0f}",
                f"{result['iv30_rv30']:.3f}",
                f"{result['ts_slope_0_45']:.6f}"
            ],
            "Status": [
                "✅ PASS" if avg_volume_pass else "❌ FAIL",
                "✅ PASS" if iv30_rv30_pass else "❌ FAIL",
                "✅ PASS" if ts_slope_pass else "❌ FAIL"
            ]
        }
        
        criteria_df = pd.DataFrame(criteria_data)
        st.dataframe(criteria_df, use_container_width=True, hide_index=True)
        
        # Charts
        st.subheader("📈 Charts")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            iv_chart = create_iv_chart(result['dtes'], result['ivs'])
            st.plotly_chart(iv_chart, use_container_width=True)
        
        with chart_col2:
            price_chart = create_price_chart(result['price_history'])
            st.plotly_chart(price_chart, use_container_width=True)
        
        # Additional metrics
        with st.expander("🔍 Additional Details"):
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.metric("Realized Volatility (30d)", f"{result['rv30']:.3f}")
                st.metric("Term Structure Slope", f"{result['ts_slope_0_45']:.6f}")
            
            with detail_col2:
                st.metric("IV30", f"{result['ivs'][0] if result['ivs'] else 'N/A':.3f}")
                st.metric("Days to First Expiration", f"{result['dtes'][0] if result['dtes'] else 'N/A'}")


if __name__ == "__main__":
    main()