from money_parser import price_dec
from bs4 import BeautifulSoup
import re

MAX_ACCEPTED_PRICE = 50000
MIN_ACCEPTED_PRICE = 50
MIN_ACCEPTED_SIZE = 34
MAX_ACCEPTED_SIZE = 45

def price_is_in_range(price):
    return price < MAX_ACCEPTED_PRICE and price > MIN_ACCEPTED_PRICE


def price_normalize(price_str):
    # try initial default (roubust) parse
    try:
        price = price_dec(price_str)
    except Exception as e:
        print(e)
        return 0.0

    if price_is_in_range(price):
        return float(price)
    else:
        return 0.0

def html_text_normalize(text):
    if type(text) is list:
        text = " ".join(text)
    # Strip HTML tags and replace with space
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = text.replace(u'\xa0', '')
    # Remove enters and trailing spaces
    text = text.replace('\n', '')
    # Add space before cap words which are not at the beggining
    text = re.sub(r'(?<!^)([A-Z][a-z])',r' \1', text)
    # Remove double spaces that might have been generated
    text = re.sub(' +',' ', text)
    text = text.rstrip().lstrip()
    # Remove dots or commas at the beggining
    text = re.sub('^(\.|\,)','', text)
    # Strip any final spaces
    text = text.rstrip().lstrip()
    return text

def size_is_in_range(price):
    return price < MAX_ACCEPTED_SIZE and price > MIN_ACCEPTED_SIZE

def sizes_normalize(sizes):
    if type(sizes) is not list:
        sizes = [sizes]
    if len(sizes) == 0:
        return []
    norm_sizes = list()
    for size in sizes:
        clean_size = _clean_size(size)
        if clean_size is not None:
            norm_sizes.append(clean_size)
    return list(set(norm_sizes))

def _clean_size(size):
    # Use Price normalizer
    try:
        size = int(price_dec(size))
    except Exception as e:
        print(e,size)
        return None

    if size_is_in_range(size):
        return size
    else:
        return None