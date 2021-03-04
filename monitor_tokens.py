import pandas as pd
import os
import urllib.request, urllib.error
from search_tokens import search_address_from_csv, write_token_data, token_file as found_tokens_file
monitor_tokens_file = "./monitor_tokens.csv"


def check_url(url):
    try:
        f = urllib.request.urlopen(url)
        f.close
        return True
    except:
        return False


def main():
    if os.path.exists(monitor_tokens_file):
        rdf1 = pd.read_csv(found_tokens_file, usecols=[0, 6])
        rdf1["Website"] = None
        rdf2 = pd.read_csv(monitor_tokens_file)

    else:
        rdf = pd.read_csv(found_tokens_file, usecols=[0, 6])
        rdf["Website"] = None
        write_token_data(rdf, monitor_tokens_file)


if __name__ == "__main__":
    main()
