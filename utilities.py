# utilities.py
# Functions used in the notebook of the ISTAT road accidents project.

# utilities.py
# Functions used in the notebook of the ISTAT road accidents project.

import os
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# folder where we save the raw data
folder = "data/raw/istat"

# ISTAT API: data and metadata of the dataset 41_983
url_data = "https://esploradati.istat.it/SDMXWS/rest/data/41_983"
url_metadata = "https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/41_983/latest?references=all"

# with this header the API gives us a csv instead of an xml
headers_csv = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}

# we download the data in chunks of years, so the server answers faster
chunks = [[2015, 2017], [2018, 2020], [2021, 2023], [2024, 2026]]


def download_file(url, file_name, headers=None):
    # if we already have the file, we don't call the API again
    if os.path.exists(file_name) or os.path.exists(file_name + ".empty"):
        print("already downloaded:", file_name)
        return

    attempts = 0
    while attempts < 6:
        attempts = attempts + 1

        # wait 20 seconds before each request: max 3 requests per minute
        # (after 5 requests in a minute ISTAT blocks us for 24-48 hours!)
        time.sleep(20)

        print("attempt", attempts, ":", url)
        try:
            # the server can be very slow, so we wait up to 3 hours (10800 seconds)
            r = requests.get(url, headers=headers, timeout=10800)
            print("status code:", r.status_code)

            if r.status_code == 200:
                # save the file
                f = open(file_name, "wb")
                f.write(r.content)
                f.close()
                print("saved:", file_name)
                return

            if r.status_code == 404:
                # no data for this request: we save an empty file to remember it
                f = open(file_name + ".empty", "w")
                f.close()
                print("no data:", file_name)
                return

            if r.status_code == 429:
                # too many requests: we stop everything, otherwise we get blocked
                exit("Too many requests (429). Try again in 24-48 hours.")

        except requests.exceptions.RequestException as e:
            print("error:", e)

        # if the request failed, we wait a bit more each time before trying again
        print("trying again in", 60 * attempts, "seconds")
        time.sleep(60 * attempts)

    print("download failed:", file_name)


def download_istat():
    # create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # 1. metadata (meaning of the codes and names of the municipalities)
    download_file(url_metadata, folder + "/metadata_41_983.xml")

    # 2. accidents data, one chunk of years at a time
    for chunk in chunks:
        start = chunk[0]
        end = chunk[1]
        url = url_data + "?startPeriod=" + str(start) + "&endPeriod=" + str(end)
        file_name = folder + "/accidents_" + str(start) + "_" + str(end) + ".csv"
        download_file(url, file_name, headers=headers_csv)

    # 3. put all the chunks together in one csv
    df = pd.DataFrame()
    for file_name in sorted(os.listdir(folder)):
        if file_name.startswith("accidents_") and file_name.endswith(".csv"):
            tmp_df = pd.read_csv(folder + "/" + file_name, dtype=str)
            df = pd.concat([df, tmp_df], ignore_index=True)

    df = df.drop_duplicates()
    df.to_csv("data/raw/istat_accidents_all.csv", index=False)
    print("all chunks combined:", df.shape)

#---------- SITUAS (population and area of the municipalities) ----------
 
# folder and final name of the file
situas_folder = "data/raw/situas"
situas_file = situas_folder + "/situas_comuni_2020.csv"
 
# SITUAS page with the list of municipalities at 31/12/2020
url_situas = "https://situas.istat.it/web/#/territorio/body?id=74&dateFrom=2020-12-31"
 
 
def download_situas():
    # if we already have the file, we don't open the browser again
    if os.path.exists(situas_file):
        print("already downloaded:", situas_file)
        return
 
    os.makedirs(situas_folder, exist_ok=True)
 
    # tell Chrome to save the downloads in our project folder (it needs the full path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default_directory": os.path.abspath(situas_folder)})
 
    # open Chrome and go to the SITUAS page
    driver = webdriver.Chrome(options=options)
    driver.get(url_situas)
 
    # wait for the page to load the table
    time.sleep(10)
 
    # click on the "Esporta" button (it has a fixed id)
    driver.find_element(By.ID, "dati-report-export-btn").click()
    time.sleep(2)
 
    # a menu opens with Excel / CSV / JSON: each one is a button with a title
    csv_item = driver.find_element(By.XPATH, "//button[@title='Scarica dati in formato CSV']")
 
    # a normal .click() fails because another element of the page covers the menu,
    # so we ask the browser to click it directly with JavaScript
    driver.execute_script("arguments[0].click();", csv_item)
 
    # wait until the csv file appears in the folder (max 60 seconds)
    downloaded = None
    seconds = 0
    while downloaded is None and seconds < 60:
        time.sleep(1)
        seconds = seconds + 1
        for file_name in os.listdir(situas_folder):
            # .crdownload = Chrome is still downloading the file
            if file_name.endswith(".csv"):
                downloaded = file_name
 
    driver.quit()
 
    if downloaded is None:
        print("download failed: no csv file found in", situas_folder)
        return
 
    # give the file a clear name
    os.rename(situas_folder + "/" + downloaded, situas_file)
    print("saved:", situas_file)




#lookup tables and helpers used in the notebook

from bs4 import BeautifulSoup

# names of the macro areas (SITUAS "Codice Ripartizione geografica")
macro_areas = {1: "North-West", 2: "North-East", 3: "Centre", 4: "South", 5: "Islands"}

# names of the regions (SITUAS "Codice Regione")
regions = {1: "Piemonte", 2: "Valle d'Aosta", 3: "Lombardia", 4: "Trentino-Alto Adige",
           5: "Veneto", 6: "Friuli-Venezia Giulia", 7: "Liguria", 8: "Emilia-Romagna",
           9: "Toscana", 10: "Umbria", 11: "Marche", 12: "Lazio", 13: "Abruzzo",
           14: "Molise", 15: "Campania", 16: "Puglia", 17: "Basilicata", 18: "Calabria",
           19: "Sicilia", 20: "Sardegna"}


def read_codelist(codelist_id, codes):
    # read the ISTAT metadata (xml) and return the meaning of the codes we ask for
    f = open(folder + "/metadata_41_983.xml", encoding="utf-8")
    soup = BeautifulSoup(f.read(), "xml")
    f.close()

    meanings = {}
    codelist = soup.find("Codelist", {"id": codelist_id})
    for code in codelist.find_all("Code"):
        if code["id"] in codes:
            meanings[code["id"]] = code.find("Name").text
    return meanings


# Export for Power BI 

def export_powerbi(mun, big, df, national, forecast):
    # save the 3 csv files used in the Power BI dashboard
    os.makedirs("data/processed", exist_ok=True)

    # 1. municipalities: add score and cluster (only for municipalities >= 10,000 inhabitants)
    mun_export = mun.merge(big[["code", "score", "cluster_name"]], how="left", on="code")
    mun_export["zone"] = mun_export["macro_area"].replace({"North-West": "Centre-North",
                                                           "North-East": "Centre-North",
                                                           "Centre": "Centre-North",
                                                           "South": "South", "Islands": "South"})
    mun_export["in_ranking"] = mun_export["population"] >= 10000
    mun_export["rank"] = mun_export["score"].rank(ascending=False)
    mun_export = mun_export.drop(columns=["years"])
    mun_export.to_csv("data/processed/municipalities.csv", index=False)

    # 2. one row per municipality and year
    df.to_csv("data/processed/accidents_by_year.csv", index=False)

    # 3. national totals + forecast in the same table
    national_export = national.reset_index()[["year", "accidents", "injured", "killed"]]
    national_export["type"] = "actual"
    forecast_export = forecast.rename(columns={"accidents_forecast": "accidents",
                                               "injured_forecast": "injured",
                                               "killed_forecast": "killed"})
    forecast_export["type"] = "forecast"
    national_export = pd.concat([national_export, forecast_export], ignore_index=True)
    national_export.to_csv("data/processed/national_trend.csv", index=False)

    print("municipalities.csv:", mun_export.shape)
    print("accidents_by_year.csv:", df.shape)
    print("national_trend.csv:", national_export.shape)