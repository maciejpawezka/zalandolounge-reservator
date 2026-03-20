# Zalando Lounge Reservator

Tired of waiting for a product on Zalando Lounge? This bot does it for you!

## Two Modes

### Product Reserve
Enter a product URL and sizes — the bot refreshes until your size is available and adds it to cart.

### Campaign Grab
Enter an upcoming campaign code — the bot waits for it to start, applies your filters (brand, sort), and fills your cart with up to 20 products.

## How to run

```
python main.py
```

Or use the standalone `ZalandoReservator.exe`.

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
| `browser_utils.py` | Shared Selenium helpers — browser, login, cookies |
| `reserve.py` | Product Reserve — single product reservation |
| `campaign.py` | Campaign Grab — fill cart from a campaign |
