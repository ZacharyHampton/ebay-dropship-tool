from CLI.Export import export
from uuid import uuid1
from CLI.Settings import settings
import random


class StellarAIO:
    def __init__(self):
        self.exportObject = export.Export()
        self.uuid = uuid1()
        self.settingsObject = settings.Settings()

    def convertToStellarFormat(self, orderData: dict):
        # print(orderData)
        # change formatting here

        stellarFormat = []
        for x in orderData['orders']:
            # print(x)

            tempData = {
                'profileName': x['shippingAddress']['firstName'] + " " + x['shippingAddress']['lastName'],
                'email': 'zh@' + self.settingsObject.getCatchall(),
                'phone': '623' + ''.join([str(random.randint(0, 9)) for i in range(7)]),
                'shipping': {
                    'firstName': x['shippingAddress']['firstName'],
                    'lastName': x['shippingAddress']['lastName'],
                    'country': x['shippingAddress']['country'],
                    'address': x['shippingAddress']['addressOne'],
                    'address2': x['shippingAddress']['addressTwo'],  # or ""
                    'state': x['shippingAddress']['state'],
                    'city': x['shippingAddress']['city'],
                    'zipcode': x['shippingAddress']['zipCode']
                },
                'billingAsShipping': self.settingsObject.useBuyerBilling(),
                'billing': {
                    'firstName': 'custom',
                    'lastName': 'billing',
                    'country': 'US',
                    'address': '123 main st',
                    'address2': 'unit 1111',  # or ""
                    'state': 'AZ',
                    'city': 'Payson',
                    'zipcode': '11111'
                },
                'payment': self.settingsObject.getPaymentInformation()
            }

            if self.settingsObject.useBuyerBilling():
                tempData['billing'] = tempData['shipping']
            else:
                tempData['billing'] = self.settingsObject.getBillingInformation()

            tempData['payment'] = self.settingsObject.getPaymentInformation()

            stellarFormat.append(tempData)

        self.exportObject.exportToFile(jsonData=stellarFormat, botName='StellarAIO', exportType='profiles',
                                       uuid=self.uuid)

    def exportTasks(self, orderData: dict):
        stellarFormat = []

        self.exportObject.exportToFile(jsonData=stellarFormat, botName='StellarAIO', exportType='tasks', uuid=self.uuid)
