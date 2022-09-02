class Check:
    def __init__(self, checkFunc, **checkArgs):
        if len(checkArgs) + 1 != checkFunc.__code__.co_argcount:
            message = "[+]Class Check Setting Error:用于check的 {} 函数参数与其所需参数数目(不包含需要check的响应)不符".format(checkFunc.__name__)
            raise Exception(message)
        self.checkFunc = checkFunc
        self.checkArgs = checkArgs

    def bakCheckResult(self, resp):
        result = self.checkFunc(resp, **self.checkArgs)
        return result

class checkMethod:
    @staticmethod
    def checkStatus(resp, statusCode):
        print("[+]Status_code:" + resp.status_code)
        if resp.status_code == statusCode:
            return True
        else:
            return False

    @staticmethod
    def checkTime(resp, timeOut):
        if isinstance(resp, dict):
            return resp["timeOut"] >= timeOut
        return resp.elapsed.total_seconds() >= timeOut

    @staticmethod
    def checkText(resp, checkModel, keyStr, **args):
        if checkModel == "A":
            if(resp.text.find(keyStr) != -1):
                return True
            else:
                return False
        elif checkModel == "B":
            if(resp.text != '' or len(resp.text) != 0):
                return True
            else:
                return False
        elif checkModel == "C":
            header = resp.headers.get(args["headerName"])
            if(header != None):
                if(header.find(keyStr) != -1):
                    return True
            return False
        else:
            message = "[+]Function checkMethod.checkText Error:目前并不支持 {} 模式".format(checkModel)
            raise Exception(message)