import os
import json


class Export:
    def __init__(self, directory='/Exports'):
        self.directory = directory

    def exportToFile(self, jsonData, botName, exportType, uuid):
        localDir = os.getcwd() + self.directory + '/{}/{}'.format(botName, uuid)

        if not os.path.exists(localDir):
            os.makedirs(localDir)

        with open(localDir + '/{}.json'.format(exportType), "w+") as f:
            f.write(json.dumps(jsonData, indent=4, sort_keys=False))
