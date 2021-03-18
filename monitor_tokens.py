import pandas as pd
import os
import urllib.request
import urllib.error
import requests
from concurrent import futures
import numpy as np
from bs4 import BeautifulSoup
import re
from search_tokens import search_address_from_csv, write_token_data, token_file as found_tokens_file, generate_soup
monitor_tokens_file = "./monitor_tokens_test.csv"
domains = [".com", ".org", ".app", ".io",
           ".finance", ".farm", ".net", ".money"]
add_netlocs = ["", "swap", "finance", "farm"]

filter_list = ["Token", "token", "TOKEN", "Swap", "swap", "SWAP", "Finance", "finance", "FINANCE", "t.me/", "BSC", "Farm", "farm",
               "FARM", ".net", ".Net", ".NET", ".com", ".COM", ".finance", ".Finance", ".FINANCE", ".io", ".farm", ".Farm", ".FARM", "_", "|"]
html_filter = ["Binance", "binance", "Farm", "farm", "swap", "Swap", "BEP20", "exchange", "Exchange", "Contract", "contract",
               "DeFi", "BTC", "btc", "Staking", "staking", "Pool", "pool", "Yield", "yield", "TOKEN", "Token", "token", "Hokder", "holder"]


def check_url(url):
    try:
        f = urllib.request.urlopen(url, timeout=5)
        f.close

        html = requests.get(url, timeout=5)
        for filter_word in html_filter:
            if filter_word in html.text:
                print("Found URL:"+url)
                return url
            else:
                return ""
    except:
        return ""


def main():
    if os.path.exists(monitor_tokens_file):

        # add new tokens
        monitor_tokens_df = pd.read_csv(monitor_tokens_file).loc[:, [
            "Address", "TokenTracker", "Website"]]
        #found_tokens_df = pd.read_csv(found_tokens_file, usecols=[0, 6])
        #found_tokens_df["Website"] = pd.Series()
        #monitor_tokens_df = monitor_tokens_df.append(
        #    found_tokens_df).drop_duplicates("Address")

        # make url lists
        url_check_dict = {}
        for token, token_address in zip(monitor_tokens_df["TokenTracker"].tolist(), monitor_tokens_df["Address"].tolist()):
            phrase = token.split(" ")[:-1]
            phrase = [w for w in phrase if w not in filter_list]
            for f in filter_list:
                phrase = [w.replace(f, "") for w in phrase]
            url_list = []
            for domain in domains:
                for add_netloc in add_netlocs:
                    url = "http://" + ''.join(phrase) + add_netloc + domain
                    url_list.append(url)
            url_check_dict[token_address] = url_list

        # check the url

        # singleprocess
        # for i, url_list in enumerate(url_check_list):
        #    print(monitor_tokens_df["TokenTracker"][i])
        #    for url in url_list:
        #        if check_url(url):
        #            monitor_tokens_df.iloc[i, -1] = url

        # multiprocess
        for token_address, url_list in url_check_dict.items():
            token_address = token_address.replace(" ", "")
            idx = monitor_tokens_df["Address"].str.contains(
                token_address).tolist().index(True)
            worker_results = []
            with futures.ProcessPoolExecutor() as executor:
                mappings = {executor.submit(check_url, url): url for url in url_list}
                for future in futures.as_completed(mappings):
                    worker_results.append(future.result())
            result_url = [result for result in worker_results if len(result)]

            # ilocで要素とらないと要らないものまでついてくる。
            website = monitor_tokens_df.iloc[idx, 2]
            if pd.isnull(website):
                monitor_tokens_df.iloc[idx, 2] = result_url
            elif result_url in website:
                pass
            else:
                monitor_tokens_df.iloc[idx, 2] = website + " " + result_url
        monitor_tokens_df.set_index("Address", inplace=True)
        monitor_tokens_df.to_csv(monitor_tokens_file)
    else:
        found_tokens_df = pd.read_csv(found_tokens_file, usecols=[0, 6])
        found_tokens_df["Website"] = None
        write_token_data(found_tokens_df, monitor_tokens_file)


if __name__ == "__main__":
    while True:
        main()