# Finance Playground

A collection of Jupyter notebooks and tools for analyzing financial securities, with a focus on risk management and return analysis. This repository contains various analyses of stocks, options, and other securities using Python.

## Notebooks

### Sector ETF Performance Analysis (`sector_etf_performance.ipynb`)

This notebook provides comprehensive analysis of sector ETF performance:

- Compares sector ETFs against the S&P 500 (SPY) over different time horizons (1, 5, 10, and 20 years)
- Analyzes relative performance ratios between sectors and the broad market
- Includes visualization of sector performance trends
- Features buy-and-hold strategy analysis across different sectors
- Covers major sector ETFs including:
  - Technology (XLK)
  - Energy (XLE)
  - Financials (XLF)
  - Healthcare (XLV)
  - And other major sectors

### Tech Research Agent (`tech-research-agent.ipynb`)

A tool that leverages AI to analyze and research technology companies:

- Uses Google's Gemini AI model for analysis
- Integrates with Serper for web search capabilities
- Helps in gathering and analyzing information about tech companies
- Useful for fundamental analysis and market research

## Requirements

- Python 3.11+
- Key dependencies:
  - yfinance
  - pandas
  - matplotlib
  - langchain
  - google-generativeai
  - crewai

## Getting Started

1. Clone this repository
2. Install the required dependencies
3. Open the notebooks in Jupyter Lab or your preferred Jupyter environment
4. For the tech research agent, you'll need to set up API keys for Google AI Studio and Serper

## Note

This repository is for educational and research purposes. Always do your own due diligence before making any investment decisions.
