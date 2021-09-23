import json
import os


class Settings:
    def __init__(self, configFile='settings.json'):
        self.configFile = configFile
        
    def useBuyerBilling(self) -> bool:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)['General']['useBuyerBilling']
    
    def getPaymentInformation(self) -> dict:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)['Payment']

    def getBillingInformation(self) -> dict:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)['Billing']
    
    def getCatchall(self) -> str:
        with open(f'{os.getcwd()}/{self.configFile}', ) as f:
            return json.load(f)['General']['catchall']
