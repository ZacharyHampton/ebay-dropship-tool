import json
import urllib.parse
import requests
import os
import base64


class EBay:
    def __init__(self, configFile='ebay.json', environment='production'):
        self.configFile = configFile
        self.environment = environment
        self.rootURL = {
            "production": {
                "auth": "https://auth.ebay.com",
                "api": "https://api.ebay.com"
            },
            "sandbox": {
                "auth": "https://auth.sandbox.ebay.com",
                "api": "https://api.sandbox.ebay.com"
            }
        }

    def getClientId(self) -> str:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)[self.environment]['appId']

    def getClientSecret(self) -> str:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)[self.environment]['certId']

    def getRedirectId(self) -> str:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)[self.environment]['redirectId']

    def getBasicToken(self) -> str:
        message = f'{self.getClientId()}:{self.getClientSecret()}'
        return base64.b64encode(bytes(message, 'ascii')).decode('ascii')

    def getRefreshToken(self) -> str:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)[self.environment]['refreshToken']

    def getBearerViaRefreshToken(self) -> str:
        refreshToken = self.getRefreshToken()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.getBasicToken()}',
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refreshToken,
            'scope': "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
        }

        response = requests.post(f'{self.rootURL[self.environment]["api"]}/identity/v1/oauth2/token', headers=headers,
                                 data=data)

        if "error" in response.json():
            raise Exception(response.json()['error_description'])

        return response.json()['access_token']

    def getBearer(self, authorizationCode) -> str:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.getBasicToken()}',
        }

        data = {
            'grant_type': 'authorization_code',
            'code': authorizationCode,
            'redirect_uri': self.getRedirectId(),
        }

        response = requests.post(f'{self.rootURL[self.environment]["api"]}/identity/v1/oauth2/token', headers=headers,
                                 data=data)

        if "error" in response.json():
            raise Exception(response.json()['error_description'])

        with open(f'{os.getcwd()}/{self.configFile}', "r") as f:
            data = json.load(f)
            data[self.environment]['refreshToken'] = response.json()['refresh_token']

        with open(f'{os.getcwd()}/{self.configFile}', "w") as f:
            json.dump(data, f)

        return response.json()['access_token']

    def generateAuthURL(self) -> str:
        urlParams = {
            'client_id': self.getClientId(),
            'redirect_uri': self.getRedirectId(),
            'response_type': 'code',
            'scope': "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
            'state': "AUTH|production|0|/my/auth?env=production&index=0&auth_type=oauth"
        }

        return f"{self.rootURL[self.environment]['auth']}/oauth2/authorize?{urllib.parse.urlencode(urlParams)}"

    def getOrders(self, bearerToken) -> dict:
        response = requests.get(
            f'{self.rootURL[self.environment]["api"]}/sell/fulfillment/v1/order?filter=orderfulfillmentstatus:%7BNOT_STARTED%7CIN_PROGRESS%7D',
            headers={'Authorization': f"Bearer {bearerToken}"})
        return response.json()

    def getOrderById(self, orderId, bearerToken) -> dict:
        response = requests.get(f'{self.rootURL[self.environment]["api"]}/sell/fulfillment/v1/order/{orderId}',
                                headers={'Authorization': f"Bearer {bearerToken}"})
        return response.json()


def getName(indivOrder: dict) -> list:
    return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['fullName'].split(' ')


def getAddressOne(indivOrder: dict) -> str:
    return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['addressLine1']


def getAddressTwo(indivOrder: dict) -> str:
    if "addressLine2" in indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']:
        return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['addressLine2']
    else:
        return ""


def getCity(indivOrder: dict) -> str:
    return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['city']


def getState(indivOrder: dict):
    if "stateOrProvince" in indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']:
        return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['stateOrProvince']
    else:
        return None


def getZipCode(indivOrder: dict):
    if "postalCode" in indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']:
        return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['postalCode'][:5]
    else:
        return None


def getCountryCode(indivOrder: dict) -> str:
    return indivOrder['fulfillmentStartInstructions'][0]['shippingStep']['shipTo']['contactAddress']['countryCode']

