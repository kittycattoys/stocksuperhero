import streamlit as st
import streamlit.components.v1 as components

# Function to display the TradingView widget for a single stock (simplified version)
def show_single_stock_widget(symbol, width=350, is_transparent=True, color_theme="dark", locale="en"):
    widget_code = f"""
    <div style="display: flex; align-items: left; justify-content: left; float: left; margin-top: -52px; pointer-events: none;">
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span class="blue-text"></span>
        </a>
      </div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>
      {{
      "symbol": "{symbol}",
      "width": {width},
      "isTransparent": {"true" if is_transparent else "false"},
      "colorTheme": "{color_theme}",
      "locale": "{locale}"
      }}
      </script>
    </div>
    </div>   
    """
    components.html(widget_code)


# Function to display the TradingView ticker tape widget
def show_ticker_tape(is_transparent=True, color_theme="dark", locale="en"):
    ticker_code = f"""
    <div style="margin-right: -50px; pointer-events: none;">
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span class="blue-text"></span>
        </a>
      </div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {{
        "symbols": [
          {{
            "proName": "NYSE:MCD",
            "title": "McDonalds"
          }},
          {{
            "proName": "NASDAQ:AAPL",
            "title": "Apple"
          }},
          {{
            "proName": "NASDAQ:SBUX",
            "title": "Starbucks"
          }},
          {{
            "proName": "NYSE:C",
            "title": "Citi"
          }},
          {{
            "proName": "NYSE:BA",
            "title": "Boeing"
          }}
        ],
        "showSymbolLogo": true,
        "isTransparent": {"true" if is_transparent else "false"},
        "colorTheme": "{color_theme}",
        "displayMode": "adaptive",
        "locale": "{locale}"
      }}
      </script>
    </div>
    </div>
    """
    components.html(ticker_code)