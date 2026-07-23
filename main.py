from fastapi import FastAPI
import pandas as pd

from scraper import scrape_diamonds

app = FastAPI(
    title="Brilliance Diamond Scraper API",
    version="1.0"
)


SHAPES = [
    "ROUND",
    "PEAR",
    "OVAL",
    "CUSHION",
    "EMERALD",
    "PRINCESS",
    "RADIANT",
    "HEART",
    "MARQUISE",
    "ASSCHER"
]


@app.get("/")
def home():

    return {
        "message": "Brilliance Diamond Scraper API is Running"
    }



@app.get("/scrape")
def scrape(
    shape: str = "ROUND",
    total: int = 10000
):

    df = scrape_diamonds(
        shape.upper(),
        total
    )


    return {

        "status":"success",

        "shape":shape.upper(),

        "records_scraped":len(df)

    }



@app.get("/scrape-all")
def scrape_all():

    all_data=[]


    for shape in SHAPES:


        print("="*60)
        print("Scraping:",shape)
        print("="*60)


        df = scrape_diamonds(

            shape,

            total=10000

        )


      


        all_data.append(df)



    final_df = pd.concat(

        all_data,

        ignore_index=True

    )


    final_df.to_csv(

        "brilliance_all_diamonds.csv",

        index=False

    )


    return {


        "status":"success",

        "message":"All shapes scraped",

        "total_records":len(final_df),

        "csv_file":"brilliance_all_diamonds.csv"

    }