import time
import requests as res

class Request:
    def __init__(self, url, method, 
    params = None, data = None, cookies = None, 
    headers = None,files = None, json = None, 
    timeOut = 0.3, URLencode = True, allowRedirect = True, waitTime = 0.3):
        self.method = method
        self.url = self.rawUrl = url
        self.rawParams, self.rawData = self.params, self.data = RequestUtils.urlencode(params, data) if URLencode  and not files else params, data
        self.rawJson = self.json = json
        self.rawCookies = self.cookies = cookies
        self.rawHeaders = self.headers = headers
        self.rawFiles = self.files = files
        self.timeOut = timeOut
        self.allowRedirect = allowRedirect
        self.waitTime = waitTime
        self.PrePayloadFunc = None

    def mainReq(self, session = None):
        #发送主要的payload请求,并返回对应响应
        resp = None
        try:
            sendMethod = getattr(session, self.method) if session else getattr(res, self.method)
            resp = sendMethod(url = self.url, 
            params = self.params, data = self.data, json = self.json, files = self.files, 
            cookies = self.cookies, headers = self.headers, 
            timeout = self.timeOut, allow_redirects = self.allowRedirect)
        except res.exceptions.RequestException:
            return {"timeOut":self.timeOut}
        except BaseException as e:
            message = "[+]请求发生错误:{}".format(e)
            raise Exception(message)
        finally:
            time.sleep(self.waitTime)
        return resp

    def send(self, session = None, **args):
        #用来提供一个可供重写的方法,便于实现如二次注入等需要前置请求操作的Payload
        if self.PrePayloadFunc == None:
            message = "[+]Class Request Setting Error:当前 Request 未设置对应Payload处理函数"
            raise Exception(message)
        self.PrePayloadFunc(self, **args)
        resp = self.mainReq()
        return resp
            
    def setPrePayloadFunc(self, func):
        self.PrePayloadFunc = func 

class RequestUtils:
    @staticmethod
    def urlencode(*args):
        encodedArgs = []
        for pos in range(len(args)):
            arg = args[pos]
            if isinstance(arg, str):
                encodedArgs.append(RequestUtils.urlencodeStr(arg))
            elif isinstance(arg, tuple):
                message = "[+]Function Request.urlencode Error:目前不支持对 tuple 类型进行URL编码"
                raise Exception(message)
            elif isinstance(arg, dict):
                encodedArgs.append(RequestUtils.urlencodeDict(arg))
        return encodedArgs[0] if len(encodedArgs) == 1 else encodedArgs

    @staticmethod
    def urlencodeStr(rawStr, blacklist = None):
        #注意这里没有采用 strip 剔除
        repreareStr = b''
        for letter in rawStr:
            if ord(letter) > 255:
                repreareStr += letter.encode('utf-8')
            else:
                repreareStr += letter.encode('latin1')
        encodedStr = b''
        blackChars = blacklist if blacklist else "?& @#%=".encode('utf-8')
        for letter in repreareStr:
            if letter in blackChars or letter < 32 or letter > 126:
                encodedStr += ('%' + '0' * (4 - len(hex(letter))) + hex(letter)[2:]).encode('utf-8')
            else:
                encodedStr += chr(letter).encode()
        return encodedStr.decode('utf-8')

    @staticmethod
    def urlencodeDict(rawDict):
        encodedStr = ''
        pos = 0
        for key, value in rawDict.items():
            if not isinstance(key, str) and not isinstance(value, str):
                message = "[+]Function Request.urlencodeDict Error:目前仅支持对键与值均 str 类型的 dict 进行URL编码"
                raise Exception(message)
            encodedStr += '&' if pos != 0 and pos != len(rawDict) else ''
            pos +=1
            encodedStr += RequestUtils.urlencodeStr(key) + '='
            encodedStr += RequestUtils.urlencodeStr(value)
        return encodedStr

    @staticmethod
    def urlencodeTuple(rawTuple):
        message = "[+]Function Request.urlencodeTuple Error:该函数功能建设中,目前不支持使用"
        raise Exception(message)