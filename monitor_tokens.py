import pandas as pd
import os
import urllib.request, urllib.error
import re
from search_tokens import search_address_from_csv, write_token_data, token_file as found_tokens_file
monitor_tokens_file = "./monitor_tokens.csv"


def check_url(url):
    try:
        f = urllib.request.urlopen(url)
        f.close
        print(url)
        return True
    except:
        return False


def main():
    schemes = ["http://", "https://"]
    domains = [".com", ".org", ".app", ".io", ".finance", ".farm", ".net"]
    filter_list = ["Token", "token", "TOKEN", "Swap", "swap", "SWAP", "Finance", "finance", "FINANCE", "t.me/", ".", "BSC"]
    if os.path.exists(monitor_tokens_file):
        rdf2 = pd.read_csv(monitor_tokens_file)
        for token in rdf2["TokenTracker"]:
            phrase = token.split(" ")[:-1]
            phrase = [w for w in phrase if w not in filter_list]
            for f in filter_list:
                phrase = [w.replace(f, "") for w in phrase]
            for scheme in schemes:
                for domain in domains:
                    url = scheme + ','.join(phrase) + domain
                    check_url(url)

    else:
        rdf = pd.read_csv(found_tokens_file, usecols=[0, 6])
        rdf["Website"] = None
        write_token_data(rdf, monitor_tokens_file)


if __name__ == "__main__":
    main()
