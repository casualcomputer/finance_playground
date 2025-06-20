# Streamlit earnings calendar calculator for options

1. Add secrets to .streamlit/secrets.toml in the format:

```
ALPHA_VANTAGE_API_KEY = "your_key_here"
POLYGON_API_KEY = "your_key_here"  
IEX_API_KEY = "your_key_here"
```

Or if running env vars:

```
export ALPHA_VANTAGE_API_KEY="your_key_here"
export POLYGON_API_KEY="your_key_here"
export IEX_API_KEY="your_key_here"
```


2. Create a virtual environment 

`source venv/bin/activate`

`pip install -r requirements.txt`

`python calculator.py`


----

Original Repo:

Join the discord for support with any of this:
https://discord.gg/krdByJHuHc


Trade calculator:
Python file and library requirements are in "trade calculator" directory
I built and tested it on Python version 3.10.11
Instructions to install and run python scripts: https://docs.google.com/document/d/1BrC7OrSTBqFs5Q-ZlYTMBJYDaS5r5nrE0070sa0qmaA/edit?tab=t.0#heading=h.tfjao7msc0g8
If these instructions aren't enough there are a lot of youtube videos concerning this. Or come to discord and ask.


Monte Carlo / Backtest Results:
https://docs.google.com/document/d/1_7UoFIqrTftoz-PJ0rxkttMc24inrAbWuZSbbOV-Jwk/edit?tab=t.0#heading=h.kc4shq41bugz


Trade Tracker Template:
https://docs.google.com/spreadsheets/d/1z_PMFqmV_2XqlCcCAdA4wgxqDg0Ym7iSeygNRpsnpO8/edit?gid=0#gid=0
Go to file and make a copy or download it for excel (only tested in google sheets)