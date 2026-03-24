import asyncio
import sys
import undetected_chromedriver as uc
from driver_utils import TabManager, create_stealth_driver
import random
from tqdm import tqdm
from openpyxl import Workbook

def product_to_row(item: dict) -> list:
    characteristics = "\n".join(
        f"{k}: {v}" for k, v in (item.get("characteristics") or {}).items()
    )
    return [
        item.get("link"),
        item.get("id"),
        item.get("name"),
        item.get("product_price"),
        item.get("description"),
        ", ".join(item.get("images") or []),
        characteristics,
        item.get("brand"),
        item.get("brand_link"),
        ", ".join(item.get("sizes") or []),
        item.get("remains"),
        item.get("reviewRating"),
        item.get("count_feedbacks"),
    ]


def js_GET_fetch_template(url: str) -> str:
    return f"""
        return fetch("{url}", {{
            method: 'GET',
            headers: {{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.wildberries.ru/',
                'X-Requested-With': 'XMLHttpRequest'
            }}
        }}).then(res => res.json());
    """


def get_basket_number(s: int) -> str:
    if 0 <= s <= 143:
        return "01"
    elif s <= 287:
        return "02"
    elif s <= 431:
        return "03"
    elif s <= 719:
        return "04"
    elif s <= 1007:
        return "05"
    elif s <= 1061:
        return "06"
    elif s <= 1115:
        return "07"
    elif s <= 1169:
        return "08"
    elif s <= 1313:
        return "09"
    elif s <= 1601:
        return "10"
    elif s <= 1655:
        return "11"
    elif s <= 1919:
        return "12"
    elif s <= 2045:
        return "13"
    elif s <= 2189:
        return "14"
    elif s <= 2405:
        return "15"
    elif s <= 2621:
        return "16"
    elif s <= 2837:
        return "17"
    elif s <= 3053:
        return "18"
    elif s <= 3269:
        return "19"
    elif s <= 3485:
        return "20"
    elif s <= 3701:
        return "21"
    elif s <= 3917:
        return "22"
    elif s <= 4133:
        return "23"
    elif s <= 4349:
        return "24"
    elif s <= 4565:
        return "25"
    elif s <= 4877:
        return "26"
    elif s <= 5189:
        return "27"
    elif s <= 5501:
        return "28"
    elif s <= 5813:
        return "29"
    elif s <= 6125:
        return "30"
    elif s <= 6437:
        return "31"
    elif s <= 6749:
        return "32"
    elif s <= 7061:
        return "33"
    elif s <= 7373:
        return "34"
    elif s <= 7685:
        return "35"
    elif s <= 7997:
        return "36"
    elif s <= 8309:
        return "37"
    elif s <= 8741:
        return "38"
    elif s <= 9173:
        return "39"
    elif s <= 9605:
        return"40"
    
    return "41"

def fetch_products_page(driver:uc.Chrome,tabs:TabManager, query, page, sort):
    # tabs.switch_to("wb")
    params = {
        "ab_testing": "false",
        "appType": 1,
        "curr": "rub",
        "dest": "12358536", #NN
        "lang": "ru",
        "page": page,
        "query": query,
        "resultset": "catalog",
        "sort": sort  # priceup, pricedown, rate, popular (def)
    }
    
    url_params = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"https://www.wildberries.ru/__internal/search/exactmatch/ru/common/v18/search?{url_params}"
    
    
    try:
        return driver.execute_script(js_GET_fetch_template(url))
    except Exception as e:
        print(f"Error fetching data from Wildberries: {e}")
        return {}
    

async def fetch_product(driver:uc.Chrome,tabs:TabManager, base_url, id):
    # tabs.switch_to("wb")
    url = f"{base_url}/info/ru/card.json"

    # params = {
    #     "ab_testing": "false",
    #     "appType": 1,
    #     "curr": "rub",
    #     "spp": 30,
    #     "dest": "-1", #full rus
    #     "lang": "ru",
    #     "hide_vflags": "4294967296",
    #     "nm": id
    # }
    # url_params = "&".join([f"{k}={v}" for k, v in params.items()])
    # url_detail = f"https://www.wildberries.ru/__internal/card/cards/v4/detail?{url_params}"

    try:
        data = driver.execute_script(js_GET_fetch_template(url))
        # detail = driver.execute_script(js_GET_fetch_template(url_detail))
        # if detail:
        #     product_detail = (detail.get("products") or [{}])[0]
        #     data["detail"] = product_detail
        return data
    except Exception as e:
        print(f"Error fetching data product: {e}")
        return {}


async def parse_wildberries_selenium(driver:uc.Chrome,tabs:TabManager, query, page, sort, pbar=None):
    data_page = fetch_products_page(driver, tabs, query, page, sort)
    
    if not data_page:
        return [], 0 
    
    total = data_page.get("total", 0)
    products = data_page.get("products", [])
    result = []
    
    for product in products:
        sizes = product.get("sizes", [])
        if not sizes:
            continue

        product_id = product.get("id")
        pics = product.get("pics", 0)
        price_info = sizes[0].get("price", {})
        # basic_price = price_info.get("basic", 0) / 100
        product_price = price_info.get("product", 0) / 100
        # discount_percent = round((1 - product_price / basic_price) * 100, 2) if basic_price else 0
        
        vol = product_id // 100000
        part = product_id // 1000
        basket = get_basket_number(vol)
        base_url = f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}"
        image_url = f"{base_url}/images/big"
        data_products = await fetch_product(driver,tabs,base_url, product_id)
        
        result.append({
            "link": f"https://www.wildberries.ru/catalog/{product.get('id')}/detail.aspx",
            "id": product_id,
            "name": product.get("name"),
            "product_price": product_price,
            "description": data_products.get("description"),
            "images": [f"{image_url}/{i}.webp" for i in range(1, pics + 1)],
            "characteristics": {
                opt["name"]: opt["value"]
                for opt in (data_products.get("options") or [])
                if opt.get("name") and opt.get("value")
            },
            "brand": product.get("brand"),
            "brand_link": f"https://www.wildberries.ru/brands/{product.get("brandId")}", 
            "sizes": [s.get("origName") or s.get("name") for s in sizes if s.get("name")],
            "remains": product.get("totalQuantity"),
            "reviewRating": product.get("reviewRating"),
            "count_feedbacks": product.get("feedbacks"),
            # "basic_price": basic_price,
            # "discount_percent": discount_percent,
            # "store": "wildberries"
        })
        if pbar:
            pbar.update(1)
            if pbar.n >= pbar.total:
                break
        # await asyncio.sleep(random.uniform(0.1, 0.3)) #wOut proxy\rotation for max stable
    
    return result, total

async def parse_all_pages(driver: uc.Chrome, tabs: TabManager, query: str, sort: str, filename: str):
    
    HEADERS = [
        "Ссылка", "Артикул", "Название", "Цена", "Описание",
        "Изображения", "Характеристики", "Селлер", "Ссылка на селлера",
        "Размеры", "Остатки", "Рейтинг", "Кол-во отзывов"
    ]

    wb = Workbook(write_only=True)
    ws = wb.create_sheet(query[:31])
    ws.append(HEADERS)

    total_saved = 0
    pbar_total = None

    with tqdm(
        total=100,
        desc="products",
        dynamic_ncols=True,  
        mininterval=0.1,     
        miniters=1,          
        file=sys.stderr      
    ) as pbar:
        page = 1
        while True:
            page_results, total = await parse_wildberries_selenium(driver, tabs, query, page, sort, pbar)

            if not page_results:
                pbar.write(f"page {page}: is empty")
                break
            
            if pbar_total is None:
                pbar_total = total
                pbar.total = total

            for item in page_results:
                ws.append(product_to_row(item))
                total_saved += 1

            if total_saved >= pbar_total:
                break

            pbar.set_postfix({"saved": total_saved})

            page += 1
            await asyncio.sleep(random.uniform(0.4, 1.1))

    wb.save(filename)

if __name__ == "__main__":
    query = "пальто из натуральной шерсти"
    
    driver, tabs = create_stealth_driver()
    filename = f"wildberries_{query}_selenium.xlsx"
    # tabs.switch_to("wb")
    try:
        asyncio.run(parse_all_pages(driver, tabs, query, "popular", filename))

        import pandas 
        df = pandas.read_excel(filename)
        filtered = df[
            (df["Рейтинг"] > 4.5) &
            (df["Цена"] <= 10000)&
            (df["Характеристики"].str.contains("Страна производства: Россия", na=False))
        ]
        filtered.to_excel(f"{query}_filtered.xlsx", index=False)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()    