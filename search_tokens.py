import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os
import schedule

options = Options()
options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=options, executable_path="c:\\chromedriver\\chromedriver.exe")
driver.set_page_load_timeout(10)
entry = "https://bscscan.com"
scrape_url = "https://bscscan.com/contractsVerified"
token_file ="./found_tokens.csv"


def generate_url(url):
    while True:
        try:
            driver.get(scrape_url)
            break
        except:
            print("TIMEOUT ERROR: target url is {}.".format(url))
            time.sleep(3)
    elem_search_btn = driver.find_element_by_xpath("/html/body/div[1]/main/div[2]/div[1]/div[2]/div/div/form/div[3]/div/span/select/option[4]")
    elem_search_btn.click()
    html = driver.page_source.encode("utf-8")
    return html


def generate_soup(url, driver_html=None):
    while True:
        try:
            html = requests.get(url, timeout=3.5)
            break
        except:
            print("TIMEOUT ERROR: target url is {}.".format(url))
            time.sleep(3)
    soup = BeautifulSoup(html.content, "html.parser")
    if driver_html is not None:
        soup = BeautifulSoup(driver_html, "html.parser")
    return soup


def url_extract(address):
    address = address.replace(" ", "")
    url = entry + "/address/" + address + "#code"
    return url


def token_filter(contract):
    soup = generate_soup(contract["Url"])
    # 条件1: TokenTrackerが存在してるか
    exist_token = soup.find_all("div", {"id": "ContentPlaceHolder1_tr_tokeninfo"})
    if exist_token:
        contract["TokenTracker"] = exist_token[0].find("a").text
        return True
    else:
        return False


def search_address_from_csv(address, data_df):
    address = address.replace(" ", "")
    if data_df is None:
        return True
    result = data_df[data_df["Address"].str.contains(address)]
    if result.empty:
        return True
    else:
        return False


def write_token_data(data_df, token_file):
    if not data_df.empty:
        data_df.set_index("Address", inplace=True)

    wait = True
    while wait:
        try:
            if os.path.exists(token_file):
                data_df.to_csv(token_file, mode="a", header=False)
            else:
                data_df.to_csv(token_file)
            wait = False
        except PermissionError:
            print("Permission Error. can't read the csv.")
            time.sleep(5)
            wait = True


def read_token_data():
    try:
        data_df = pd.read_csv(token_file, usecols=[0])
    except FileNotFoundError:
        return None
    return data_df


def job():
    soup = generate_soup(scrape_url, driver_html=generate_url(scrape_url))
    raw_contract_list = soup.find("tbody").find_all("tr")
    dt_now = datetime.datetime.now()
    rdf = read_token_data()
    extract_contracts = [
        {"Address": elem.contents[0].text, "Timestamp": dt_now, "Url": url_extract(elem.contents[0].text),
         "Name": elem.contents[1].text, "Txns": elem.contents[5].text, "Verified": elem.contents[7].text,
         "TokenTracker": None} for elem in raw_contract_list if search_address_from_csv(elem.contents[0].text, rdf)]
    extract_contracts = [contract for contract in extract_contracts if token_filter(contract)]
    wdf = pd.json_normalize(extract_contracts)
    write_token_data(wdf, token_file=token_file)
    print("new tokens here {}".format(wdf))


def main():
    schedule.every(2).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()