from .utils import getCharacterSet

def BisectionMethod(requestModule, checkModule, **args):
    mode = args["mode"] if "mode" in args.keys() else 1
    result=""
    endFlag = False
    length = args["length"] if "length" in args.keys() else 50
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        prv = args["prv"] if "prv" in args.keys() else 32
        last = args["last"] if "last" in args.keys() else 126
        middle=(prv+last)//2
        if mode==1:
            while(prv<=last):
                print("[+]Testing:{}=>{}".format(num,middle))
                if(checkModule.bakCheckResult(requestModule.send(code = middle, num = num,sympol = "="))):
                    result+=chr(middle)
                    print("[+]Matched!Now result:{}".format(result))
                    break
                elif(checkModule.bakCheckResult(requestModule.send(code = middle, num = num, sympol = ">"))):
                    prv=middle+1
                else:
                    if(middle==32):
                        endFlag=True
                        break
                    last=middle-1
                middle=(prv+last)//2
        elif mode==2:
            last+=1
            while(prv<last):
                print("[+]Testing:{}=>{}".format(num,middle))
                if(checkModule.bakCheckResult(requestModule.send(code = middle, num = num, sympol = ">"))):
                    prv=middle+1
                else:
                    last=middle
                middle=(prv+last)//2
            if middle==32 and not checkModule.bakCheckResult(requestModule.send(code = 0, num = num, sympol = ">")):
                endFlag=True
                break
            result+=chr(middle)
            print("[+]Matched!Now result:{}".format(result))
    print("[+]The full result:{}".format(result))

def CharacterSetTraversal(requestModule, checkModule, **args):
    length = args["length"] if "length" in args.keys() else 50
    mode = args["mode"] if "mode" in args.keys() else "A"
    targetCharSet = getCharacterSet(args["charsetNum"]) if "charsetNum" in args.keys()  else ( args["charset"] if "charset" in args.keys() else getCharacterSet(6))
    result = ""
    endFlag = False
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        for char in targetCharSet:
            print("[+]Testing:{}=>{}".format(num,char))
            if mode=="A":
                checkFlag = checkModule.bakCheckResult(requestModule.send(char = char, num=num))
            elif mode=="B":
                checkFlag = checkModule.bakCheckResult(requestModule.send(char = result + char))
            if checkFlag:
                result+=char
                print("[+]Matched!Now result:{}".format(result))
                break
            elif char==targetCharSet[len(targetCharSet)-1:]:
                endFlag=True
                break
    print("[+]The full result:{}".format(result))


def ResultSetCrosSComparison(requestModule, checkModule, **args):
    length = args["length"] if "length" in args.keys() else 50
    targetCharSet = getCharacterSet(args["charsetNum"]) if "charsetNum" in args.keys()  else ( args["charset"] if "charset" in args.keys() else getCharacterSet(6))
    sympol = args["sympol"] if "sympol" in args.keys() else ">"
    result = ""
    endFlag = False
    for num in range(1,length):
        if endFlag:
            print("[+]Match Finished!")
            break
        for char in targetCharSet:
            print("[+]Testing:{}=>{}".format(num,char))
            checkMin = checkModule.bakCheckResult(requestModule.send(char = result + char + "!",sympol = sympol))
            checkMax = checkModule.bakCheckResult(requestModule.send(char = result + char + "~",sympol = sympol))
            checkEqual = checkModule.bakCheckResult(requestModule.send(char = result + char, sympol = "="))
            checkFlag = checkMax ^ checkMin
            print("[+]min:{} ^ max:{} => flag:{}".format(checkMin,checkMax,checkFlag))
            if checkFlag or checkEqual:
                result += char
                print("[+]Matched!Now result:{}".format(result))
                print("[+]equal:{}".format(checkEqual))
                if checkEqual:
                    endFlag = True
                break
            elif char == targetCharSet[len(targetCharSet)-1:]:
                endFlag = True
                break
    print("[+]The full result:{}".format(result))