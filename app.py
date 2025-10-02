from flask import Flask, render_template, jsonify
import requests
import threading
import time
import logging

app = Flask(__name__)

# Настройки
REFRESH_INTERVAL = 60 * 10  # обновлять каждые 10 минут
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories/"
LOCALE = "english"
CC = "UA"  # для гривны, можно менять на "US" и т.д.

# Кэш
_cached_deals = []
_last_fetch = 0
_lock = threading.Lock()

logging.basicConfig(level=logging.INFO)


def fetch_deals():
    """Получить реальные скидки из блока 'specials' + новинки из 'new_releases' и сохранить в кэш"""
    global _cached_deals, _last_fetch
    try:
        params = {"l": LOCALE, "cc": CC}
        logging.info("Fetching Steam specials and new releases...")
        r = requests.get(STEAM_FEATURED_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # ====== Специальные скидки ======
        specials_block = data.get("specials", {})
        specials_items = specials_block.get("items", [])

        items = []
        for it in specials_items:
            item = {
                "id": it.get("id"),
                "name": it.get("name"),
                "discount_percent": int(it.get("discount_percent", 0)),
                "initial": it.get("original_price"),
                "final": it.get("final_price"),
                "currency": it.get("currency", "UAH"),
                "large_capsule": it.get("large_capsule_image") or it.get("header_image") or 'https://store.cloudflare.steamstatic.com/public/images/v6/game_placeholder.png',
                "store_link": f"https://store.steampowered.com/app/{it.get('id')}"
            }
            items.append(item)

        # сортируем по убыванию скидки
        items.sort(key=lambda x: x.get("discount_percent", 0), reverse=True)

        # ====== Новые релизы ======
        new_releases_block = data.get("new_releases", {})
        new_releases_items = new_releases_block.get("items", [])

        for it in new_releases_items:
            item = {
                "id": it.get("id"),
                "name": it.get("name"),
                "discount_percent": int(it.get("discount_percent", 0)) if it.get("discount_percent") else 0,
                "initial": it.get("original_price") or it.get("initial") or None,
                "final": it.get("final_price") or it.get("final") or None,
                "currency": it.get("currency", "UAH"),
                "large_capsule": it.get("large_capsule_image") or it.get("header_image") or 'https://store.cloudflare.steamstatic.com/public/images/v6/game_placeholder.png',
                "store_link": f"https://store.steampowered.com/app/{it.get('id')}" if it.get("id") else it.get("url")
            }
            items.append(item)

        with _lock:
            _cached_deals = items
            _last_fetch = int(time.time())

        logging.info(f"Fetched {len(items)} items: specials + new releases.\n")

    except Exception as e:
        logging.exception("Error fetching deals from Steam: %s", e)


def periodic_refresher():
    """Фоновая задача: периодически обновляет кэш"""
    while True:
        fetch_deals()
        time.sleep(REFRESH_INTERVAL)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/deals")
def api_deals():
    with _lock:
        return jsonify({
            "last_fetch": _last_fetch,
            "count": len(_cached_deals),
            "items": _cached_deals,
        })


if __name__ == "__main__":
    # Первичное заполнение кэша
    fetch_deals()

    # Запуск фонового обновления
    t = threading.Thread(target=periodic_refresher, daemon=True)
    t.start()

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=5755, debug=True)
