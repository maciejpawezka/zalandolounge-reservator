# Zalando Lounge Reservator

Tired of waiting for a product on Zalando Lounge? This bot does it for you!

## How to run

```
python main.py
```

## Requirements

- Python 3.10+
- Google Chrome

Install dependencies:
```
pip install selenium webdriver-manager
```

## Project structure

| File | Description |
|------|-------------|
| `main.py` | Entry point — launches the GUI |
| `gui.py` | Graphical interface (tkinter) |
| `bot.py` | Selenium logic — login, reservation |

## How it works

1. Enter product URL, email, password, and desired sizes
2. Click START
3. The bot opens Chrome and logs in via Zalando SSO
4. Refreshes the page until the selected size becomes available
5. Adds the product to cart
