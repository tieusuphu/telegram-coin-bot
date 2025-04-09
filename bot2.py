import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CẤU HÌNH ===
CMC_API_KEY = '749f58c4-f2f3-4059-88ff-18fb487ccf26'  # <-- Thay bằng API Key từ CoinMarketCap
TELEGRAM_BOT_TOKEN = '7615567877:AAHYTtTSEnN1o19NihjG2QsXhFnsEC5Kl3g'  # <-- Thay bằng token bot Telegram

CMC_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
CMC_MAP_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

# === HÀM LẤY SLUG COIN ===
def get_coin_slug(symbol: str):
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    response = requests.get(CMC_MAP_URL, headers=headers)
    data = response.json()

    if "data" in data:
        for coin in data["data"]:
            if coin["symbol"].upper() == symbol.upper():
                return coin["slug"]
    return None

# === HÀM LẤY GIÁ COIN ===
async def get_coin_price(symbol: str):
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'symbol': symbol.upper(), 'convert': 'USD'}
    response = requests.get(CMC_API_URL, headers=headers, params=params)
    data = response.json()

    if "data" in data and symbol.upper() in data["data"]:
        coin = data["data"][symbol.upper()]
        name = coin.get("name", symbol.upper())
        quote = coin.get("quote", {}).get("USD", {})
        price = quote.get("price")
        change_24h = quote.get("percent_change_24h")

        if price is None:
            return f"⚠️ Hiện chưa có giá USD cho `{symbol.upper()}`. Coin có thể chưa được niêm yết hoặc không còn hoạt động.", None

        # Định dạng giá trị nhỏ
        if price >= 1:
            price_str = f"{price:,.2f}"
        else:
            price_str = f"{price:,.8f}".rstrip('0').rstrip('.')  # loại bỏ số 0 thừa

        if change_24h is None:
            change_24h = 0.0  # nếu không có dữ liệu thì để 0%

        arrow = "🟢" if change_24h >= 0 else "🔴"
        slug = get_coin_slug(symbol)

        text = (
            f"💰 {name} ({symbol.upper()})\n"
            f"💵 Giá hiện tại: {price_str} USD\n"
            f"{arrow} Biến động 24h: {change_24h:.2f}%"
        )

        link = f"https://coinmarketcap.com/currencies/{slug}/" if slug else None
        return text, link

    else:
        return f"❌ Không tìm thấy thông tin cho mã coin `{symbol}`.", None

# === LỆNH /p ===
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập mã coin. Ví dụ: /p BTC")
        return

    symbol = context.args[0]
    result, link = await get_coin_price(symbol)

    if link:
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Tìm hiểu thêm", url=link)]
        ])
        await update.message.reply_text(result, reply_markup=button)
    else:
        await update.message.reply_text(result)

# === KHỞI CHẠY BOT ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("p", price_command))
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
