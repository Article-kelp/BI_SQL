import string

''' str("test") => "0x74657374" '''
def str2hex(strs):
    afterStrs = "0x"
    for letter in strs:
        hexs = hex(ord(letter))
        afterStrs += "0" * (2-len(hexs[2:])) + hexs[2:]
    return afterStrs

''' 提供一些盲注可能用到的字符集 '''
def getCharacterSet(num):
    charSet={
        1:string.ascii_letters+string.digits,     #大小写26字母+数字
        2:string.digits+"abcdef"+"{}-",     #flag字符
        3:"!$&()*+,-./:;<=>?@[\]^`{|}~_%#",       #除开单双引号的标点字符
        4:string.ascii_letters+string.digits+"!$&()*+,-./:;<=>?@[\]^`{|}~_%#",   #所有除开单双引号可见字符
        5:string.ascii_lowercase+"0123456789"+"{}@,.<>=-_",    #感觉可能用的最多的
        6:string.ascii_lowercase+"0123456789"+"-._"   #5的简化版本
    }
    return charSet[num]