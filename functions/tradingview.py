import streamlit as st
import streamlit.components.v1 as components

# Function to display the TradingView widget for a single stock (simplified version)
def show_single_stock_widget(symbol, width=350, is_transparent=True, color_theme="light", locale="en"):
    """
    Embeds the TradingView Single Quote widget for a single stock symbol.
    
    Args:
        symbol (str): The stock symbol in 'EXCHANGE:SYMBOL' format.
        width (int): The width of the widget.
        is_transparent (bool): Whether the widget should be transparent.
        color_theme (str): The color theme of the widget, either 'light' or 'dark'.
        locale (str): The locale for language settings.
    """
    widget_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span class="blue-text">Track all markets on TradingView</span>
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
    <!-- TradingView Widget END -->
    """
    components.html(widget_code, height=500)


def show_ticker_tape():
    """
    Displays the TradingView ticker tape widget using Streamlit components.
    """
    ticker_code = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <div class="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span class="blue-text">Track all markets on TradingView</span>
        </a>
      </div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
        "symbols": [
          {
            "proName": "NYSE:MCD",
            "title": "McDonalds"
          },
          {
            "proName": "NASDAQ:AAPL",
            "title": "Apple"
          },
          {
            "proName": "NASDAQ:SBUX",
            "title": "Starbucks"
          },
          {
            "proName": "NYSE:C",
            "title": "Citi"
          },
          {
            "proName": "NYSE:BA",
            "title": "Boeing"
          }
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "en"
      }
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(ticker_code, height=100)