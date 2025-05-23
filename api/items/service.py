import requests


class WildberriesParser:
    BASE_URL = "https://search.wb.ru/exactmatch/ru/common/v13/search"
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
    }

    COLOR_CODES = {
        "бежевый": "16119260",
        "белый": "16119181",
        "голубой": "16227191",
        "желтый": "16119238",
        "зеленый": "16227334",
        "коричневый": "16119216",
        "красный": "16119167",
        "розовый": "16119178",
        "серый": "16119199",
        "синий": "16227200",
        "фиолетовый": "16227301",
        "черный": "16320279",
    }

    def __init__(self, search_query):
        self.search_query = search_query

    def get_products(self, color=None, price_from=None, price_to=None):
        page = 1
        products = []
        total_found = 0

        color_code = self.COLOR_CODES.get(color.lower()) if color else None

        while True:
            params = {
                "query": self.search_query,
                "resultset": "catalog",
                "sort": "popular",
                "page": page,
                "limit": 100,
                "appType": 1,
                "curr": "rub",
                "dest": "-1257786",
            }

            if color_code:
                params["fcolor"] = color_code
            if price_from is not None or price_to is not None:
                pf = int((price_from or 0) * 100)
                pt = int((price_to or 1_000_000) * 100)
                params["priceU"] = f"{pf};{pt}"

            response = requests.get(self.BASE_URL, params=params, headers=self.HEADERS, timeout=10)
            if response.status_code != 200:
                raise Exception(f"error: {response.status_code}")

            data = response.json()

            if page == 1:
                total_found = data.get("data", {}).get("total", 0)

            products_on_page = data.get("data", {}).get("products", [])
            if not products_on_page:
                break

            for item in products_on_page:
                colors = item.get("colors", [])
                colors_list = [c.get("name", "").lower() for c in colors]

                if color and color.lower() not in colors_list:
                    continue

                sizes = item.get("sizes", [])
                min_price = None
                for size in sizes:
                    price_info = size.get("price", {})
                    price_val = price_info.get("total")
                    if price_val is not None:
                        price_val_rub = price_val / 100
                        if (min_price is None) or (price_val_rub < min_price):
                            min_price = price_val_rub

                if min_price is None:
                    continue

                if price_from is not None and min_price < price_from:
                    continue
                if price_to is not None and min_price > price_to:
                    continue

                product = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "min_price": min_price,
                    "colors": colors_list,
                    "url": f"https://www.wildberries.ru/catalog/{item.get('id')}/detail.aspx"
                }
                products.append(product)

            page += 1

        return total_found, products
