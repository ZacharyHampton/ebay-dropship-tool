from ebay import ebay
from urllib.parse import unquote
from Walmart import walmart
from Export import stellaraio
from tabulate import tabulate


def conversionParser(listRange: str, dictLength: int) -> list:
    finalList = []

    if " " in listRange:
        listRange = listRange.replace(" ", "")

    if len(listRange) == 1 and listRange.isnumeric():
        if dictLength >= int(listRange) > 0:
            finalList.append(int(listRange) - 1)
            return finalList

    if "-" in listRange and "," not in listRange:
        listRange += ","

    if "," in listRange:
        commaSplits = listRange.split(',')
        for x in commaSplits:
            if "-" in x:
                if x.count("-") == 1:
                    isRangeSplit = x.split('-')
                    if isRangeSplit[0].isnumeric() and isRangeSplit[1].isnumeric():
                        if dictLength >= int(isRangeSplit[0]) > 0 and dictLength >= int(isRangeSplit[1]) > 0:
                            for y in range(int(isRangeSplit[0]) - 1, int(isRangeSplit[1])):
                                finalList.append(y)
                            continue
            elif x.isnumeric():
                finalList.append(int(x) - 1)

    return finalList


def main():
    bot = ebay.EBay()
    refreshToken = bot.getRefreshToken()

    if refreshToken != "":
        bearer = bot.getBearerViaRefreshToken()
    else:
        print("Refresh token invalid. Getting new tokens.")
        print(bot.generateAuthURL())
        authToken = input("Give us the auth token: ")
        bearer = bot.getBearer(authToken)

    orders = bot.getOrders(bearer)

    counter = 1
    uiOrder = {
        "orders": [

        ]
    }

    for x in orders['orders']:

        if x['orderPaymentStatus'] == "PAID":
            orderData = {
                'id': counter,
                'orderId': x['orderId'],
                'title': unquote(x['lineItems'][0]['title']),
                'buyerUsername': x['buyer']['username'],
                'shippingAddress': {
                    # ADD FIRST AND LAST NAME FUNCTIONS
                    'fullName': ' '.join(ebay.getName(x)),
                    'firstName': ebay.getName(x)[0],
                    'lastName': ebay.getName(x)[1],
                    'addressOne': ebay.getAddressOne(x),
                    'addressTwo': ebay.getAddressTwo(x),
                    'city': ebay.getCity(x),
                    'state': ebay.getState(x),
                    'zipCode': ebay.getZipCode(x),
                    'country': ebay.getCountryCode(x)
                }
            }

            uiOrder['orders'].append(orderData)
            counter += 1

    tabulateTable = []
    tabulateHeaders = ['ID', 'eBay Title', 'Buyer Username']
    for x in uiOrder['orders']:
        tabulateTable.append([x['id'], x['title'], x['buyerUsername']])

    print(tabulate(tabulateTable, tabulateHeaders, tablefmt="github", stralign="left"))

    choice = input('\nWhat item(s) would you like to DS? ')

    indeces = conversionParser(choice, len(uiOrder['orders']))

    dsingOrders = {
        "orders": [

        ]
    }
    for x in indeces:
        foundSKU = walmart.getSkuByTitle(uiOrder['orders'][x]['title'])
        choice = input("[{}] Is this the correct product?\n{} [y/N]: ".format(x + 1,
                                                                              "https://walmart.com/ip/SnivelingAIO/" + foundSKU))
        if choice.lower() in ['y', 'yes']:
            uiOrder['orders'][x]['walmartSKU'] = foundSKU
            dsingOrders['orders'].append(uiOrder['orders'][x])
            print('[{}] Added SKU {} to your dropshipping orders.'.format(x + 1, foundSKU))
        else:
            choice = input("[{}] Enter the SKU: ".format(x + 1))
            uiOrder['orders'][x]['walmartSKU'] = choice
            dsingOrders['orders'].append(uiOrder['orders'][x])
            print('[{}] Added SKU {} to your dropshipping orders.'.format(x + 1, choice))

    print('Exporting...')
    stellaraio.StellarAIO().convertToStellarFormat(dsingOrders)
    input('Exported!')


if __name__ == "__main__":
    main()
