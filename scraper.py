from curl_cffi import requests
import pandas as pd
import time

from config import COOKIES


BASE_URL = "https://worker.brilliance.com/api/v1/lab-grown-diamond-search"


HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://www.brilliance.com/",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149 Safari/537.36"
}


SHAPES = {
    "ROUND": 0,
    "PRINCESS": 1,
    "CUSHION": 2,
    "OVAL": 3,
    "EMERALD": 4,
    "HEART": 5,
    "PEAR": 6,
    "MARQUISE": 7,
    "ASSCHER": 8,
    "RADIANT": 9
}



def fetch_batch(shape_id, pager):


    payload = {

        "data": {

            "imgOnly": True,
            "view": "grid",

            "priceMin": 750,
            "priceMax": 100000,

            "caratMin": 1.5,
            "caratMax": 12,

            "colorMin": 6,
            "colorMax": 9,

            "clarityMin": 4,
            "clarityMax": 9,

            "depthMin": 0,
            "depthMax": 90,

            "tableMin": 0,
            "tableMax": 90,

            "shapeList": [
                shape_id
            ],

            "certificateList": [],

            "pager": pager,

            "cutMin": 0,
            "cutMax": 4,

            "polishMin": 0,
            "polishMax": 3,

            "symmetryMin": 0,
            "symmetryMax": 3,

            "fluorMin": 0,
            "fluorMax": 3,

            "fastShipping": 0

        }
    }


    response = requests.post(

        BASE_URL,

        headers=HEADERS,

        cookies=COOKIES,

        json=payload,

        impersonate="chrome",

        timeout=60

    )


    print(
        "Pager:",
        pager,
        "Status:",
        response.status_code
    )


    if response.status_code != 200:
        return []


    result = response.json()


    diamonds = result.get(
        "diamond",
        []
    )


    print(
        "Returned:",
        len(diamonds)
    )


    return diamonds




def scrape_diamonds(shape, total=10000):


    shape_id = SHAPES[shape]


    all_diamonds = []


    pager = 0



    while len(all_diamonds) < total:


        batch = fetch_batch(
            shape_id,
            pager
        )


        if not batch:

            print(
                "No more diamonds"
            )

            break



        for d in batch:


            all_diamonds.append({

                "ID": d.get("nid"),

                "Shape": d.get("shape"),

                "Price": d.get("price"),

                "Carat": d.get("carat"),

                "Color": d.get("color"),

                "Clarity": d.get("clarity"),

                "Cut": d.get("cut"),

                "Report": d.get("report"),

                "Report Number": d.get("reportNumber"),

                "Polish": d.get("polish"),

                "Symmetry": d.get("symmetry"),

                "Depth": d.get("depth"),

                "Table": d.get("table"),

                "Fluorescence": d.get("fluorescence"),

                "Measurement": d.get("measurement"),

                "URL": d.get("alias")

            })


            if len(all_diamonds) >= total:
                break



        print(
            "Collected:",
            len(all_diamonds)
        )


        pager += 1


        time.sleep(0.05)



    return pd.DataFrame(all_diamonds)