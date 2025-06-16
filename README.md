# Finance Playground

A comprehensive collection of Jupyter notebooks and tools for analyzing financial securities, implementing trading strategies, and conducting market research. This repository contains various analyses of stocks, ETFs, and other securities using Python, with a focus on quantitative analysis, risk management, and AI-powered research.

## Notebooks

### AI Hedge Fund Agents Analysis (`ai_hedge_fund_agents_analysis.ipynb`)

Comprehensive analysis and comparison of legendary hedge fund strategies and investment approaches:

- **Intrinsic Value Strategies**: Damodaran DCF, Benjamin Graham, Warren Buffett, and Phil Fisher methodologies
- **Growth & Momentum**: Cathie Wood, Stanley Druckenmiller, Peter Lynch, and Rakesh Jhunjhunwala approaches
- **Deep Value/Contrarian**: Michael Burry, Bill Ackman value investing strategies
- **Quality-Based Screens**: Fundamental screening and Charlie Munger quality metrics
- **Tactical Overlays**: Technical analysis, valuation blends, sentiment analysis, and risk management
- Detailed comparison tables showing decision steps, assumptions, required inputs, and limitations for each strategy
- Implementation roadmap for building a complete hedge fund system

### Mark Minervini Strategy Implementation (`mark_minervini__strategy_roi.ipynb`)

Complete implementation of Mark Minervini's 8-point Trend Template strategy:

- **8-Point Screening System**: Automated screening based on Minervini's trend template conditions
- **Technical Analysis**: SMA crossovers, relative strength calculations, and momentum indicators
- **Stock Screener**: Configurable screener with volume, price, and relative strength filters
- **Visualization Tools**: Price charts with moving averages and trend analysis
- **Performance Metrics**: Comprehensive stock analysis including 52-week ranges and RS ratings
- Ready-to-use Python classes for implementing the complete strategy

### ETF Risk Analysis & Comparison (`compare_etf_different_inceptions.ipynb`)

Advanced ETF analysis with comprehensive risk-adjusted performance metrics:

- **Risk-Adjusted Metrics**: Sharpe, Sortino, Treynor, Jensen's Alpha, Information Ratio
- **Advanced Risk Measures**: Maximum Drawdown, Calmar Ratio, Omega Ratio
- **Statistical Analysis**: Jarque-Bera normality tests, skewness, kurtosis analysis
- **Beta Stability**: Rolling beta analysis for stability assessment
- **Visual Analytics**: Daily returns, cumulative performance, and drawdown analysis
- **Assumption Validation**: Automatic interpretation based on statistical tests
- Focus on Canadian ETFs (ZLB.TO, XDIV.TO, XEQT.TO, VDY.TO) vs SPY benchmark

### Sector ETF Performance Analysis (`sector_etf_performance.ipynb`)

Comprehensive analysis of sector ETF performance and market dynamics:

- **Multi-Timeframe Analysis**: 1, 5, 10, and 20-year performance comparisons
- **Sector Rotation Analysis**: Relative performance ratios between sectors and broad market
- **Buy-and-Hold Strategy**: Long-term performance analysis across different sectors
- **Visualization Tools**: Ratio analysis plots and trend identification
- **Complete Sector Coverage**: All major SPDR sector ETFs (XLE, XLK, XLF, XLV, XLB, XLI, etc.)
- **Benchmarking**: Performance comparison against S&P 500 (SPY)

### Tech Research Agent (`tech-research-agent.ipynb`)

AI-powered research assistant for technology company analysis:

- **Google Gemini Integration**: Advanced AI analysis using Gemini 1.5 Flash
- **Web Search Capabilities**: Real-time information gathering via Serper API
- **CrewAI Framework**: Multi-agent system for comprehensive research
- **Automated Analysis**: Company evaluation, idea filtering, and research synthesis
- **Investment Research**: Tech startup and company analysis automation
- **Data Integration**: CSV data processing and analysis workflows

## Technical Features

### Data Sources & APIs

- **yfinance**: Real-time and historical stock/ETF data
- **Google Gemini AI**: Advanced language model for analysis
- **Serper API**: Web search and real-time information
- **pandas/numpy**: Data manipulation and numerical analysis

### Analysis Capabilities

- **Quantitative Screening**: Multi-criteria stock and ETF screening
- **Risk Management**: VaR, drawdown analysis, and risk metrics
- **Technical Analysis**: Moving averages, momentum, and trend indicators
- **Statistical Analysis**: Normality tests, correlation, and regression analysis
- **Performance Attribution**: Return decomposition and factor analysis

### Visualization Tools

- **matplotlib**: Comprehensive charting and plotting
- **Interactive Charts**: Multi-timeframe analysis and ratio plots
- **Performance Dashboards**: Risk-return scatter plots and heat maps

## Requirements

- Python 3.11+
- Key dependencies:
  - yfinance (market data)
  - pandas, numpy (data analysis)
  - matplotlib (visualization)
  - scipy (statistical analysis)
  - langchain, crewai (AI agents)
  - google-generativeai (Gemini AI)

## Getting Started

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install yfinance pandas matplotlib scipy numpy
   pip install langchain crewai google-generativeai
   ```
3. For AI features, set up API keys:
   - Google AI Studio API key for Gemini
   - Serper API key for web search
4. Open the notebooks in Jupyter Lab or Google Colab
5. Follow the documentation within each notebook for specific setup instructions

## Configuration

### Google Colab Setup

- Add your `GOOGLE_API_KEY` to Colab Secrets for Gemini AI access
- Add your `SERPER_API_KEY` to Colab Secrets for web search functionality
- All notebooks are optimized for Google Colab environment

### Local Setup

- Set environment variables for API keys
- Ensure all dependencies are installed
- Some notebooks may require additional setup for AI features

## Use Cases

- **Portfolio Management**: ETF selection and sector rotation strategies
- **Stock Screening**: Identify stocks meeting specific technical criteria
- **Risk Analysis**: Comprehensive risk-adjusted performance evaluation
- **Market Research**: AI-powered company and sector analysis
- **Strategy Backtesting**: Historical performance analysis of trading strategies
- **Educational**: Learn quantitative finance and algorithmic trading concepts

## Note

This repository is for educational and research purposes. The strategies and analyses presented are for learning and should not be considered as investment advice. Always conduct your own due diligence and consider consulting with financial professionals before making investment decisions. Past performance does not guarantee future results.

## License

This project is licensed under the terms specified in the LICENSE file.
