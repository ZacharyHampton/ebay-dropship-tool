import requests
from urllib.parse import unquote
import difflib


def getSkuByTitle(ebayTitle) -> str:
    # get products related to ebay title
    response = requests.get('https://www.walmart.com/preso/search?query=' + ebayTitle, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"})

    similarityDict = {
        "similarity": [],
        "correspondingSkus": []
    }

    for x in response.json()['items']:
        # remove html
        title = x['title']
        title = title.replace('<mark>', '')
        title = title.replace('</mark>', '')
        title = unquote(title)
        # get similarity ratio between ebay listing title and walmart product title
        simRatio = difflib.SequenceMatcher(None, ebayTitle, title).ratio()
        similarityDict['similarity'].append(simRatio)
        # appends sku, ratio, and title
        similarityDict['correspondingSkus'].append((x['id'], str(simRatio), title))

    # sort from greatest to least
    similarityDict['similarity'].sort(reverse=True)
    for x in similarityDict['correspondingSkus']:
        # if greatest similarity ratio is also in a tuple from a corresponding sku, we found the greatest possible correct product for us
        if str(similarityDict['similarity'][0]) == x[1]:
            # return sku
            return x[0]


class Walmart:
    #def __init__(self):
    #    self.name = "walmart"

    pass
