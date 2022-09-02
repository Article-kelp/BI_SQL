import time
import datetime

class Controller:
    def __init__(self, centralModule, requestModule, checkModule):
        self.requestModule = requestModule
        self.checkModule = checkModule
        self.centralModule = centralModule

    def run(self):
        startTime = time.time()
        print("[+]程序开始执行,当前时间为:{}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))))
        self.centralModule(self.requestModule, self.checkModule)
        endTime = time.time()
        print("[+]程序执行结束,当前时间为:{}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTime))))
        print("[+]共计耗时:{}".format(datetime.timedelta(seconds = endTime - startTime)))
      