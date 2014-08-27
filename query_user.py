#!/usr/bin/env python
#coding=gb2312

from downloader import * 

logger.addHandler(console)
console.setLevel(logging.DEBUG)
#################### Get query screen ###########33
def getqscr(tn):
    read_all(tn,TIMEOUT_0)
    pu = re.compile(".+\\x1b\[2;\d+H",re.S) #user query page
    pb = re.compile(".+\\x1b\[\d+;2H") #board page
    redrawcurscreen(tn)
    res = tn.expect([pu,pb],TIMEOUT_4)
    if res[0]<0:
        logger.warn("undefined status of page status")
        print res[2]
        
    return res[2]
    
def enterqscr(tn):
    logger.debug("Enter query menu")
    buf = getqscr(tn)
    res = re.search("查询谁:\s?(\w*)\\x1b\[K",buf)
    if res:
        logger.info("Already in query menu status")
        l = len(res.group(1))
        if l>0:
            tn.write("\b"*l)
            logger.info("Removed existing string "+res.group(1))
        return True
    tn.write("u")
    res = tn.expect(["查询谁:"],TIMEOUT_4)
    if res<0:
        redrawcurscreen(tn)
        buf = read_all(tn,1)
        logger.error("Can't check user now\n%s"%buf)
        print "Can't check user now\n%s"%buf
        return False
    return True
def quitqscr(tn):
    buf = getqscr(tn)
    res = re.search("查询谁:(\w*)",buf)
    if not res:
        logger.warn("Not in query status\n"+buf)
        return False
    l = len(res.group(1))
    tn.write(l*'\b' + '\n')
    buf = getqscr(tn)
    res = re.search("查询谁: (\w+)",buf)
    if not res:
        logger.info("Quit successfully from query status")
    else:
        logger.error("Failed quit from query statuts")
    
def getusers(tn,prefix):
    logger.info("Start query users starts with "+prefix)
    if len(prefix)>=13:
        prefix = prefix[:13]
        logger.warn("Prefix error, length should be in 13, cut it")
    if not enterqscr(tn):
        logger.error("Failed to enter user query screen")
        return False
    logger.info("Input query prefix "+prefix)
    tn.write(prefix)
    cursor = "\x1b[2;%sH"%(9+len(prefix))
    userstr = ""
    while True:
        tn.write("\t")
        res = tn.read_until(cursor,TIMEOUT_4)
        buf = getqscr(tn)
        poss = buf.find("所有使用者")
        pose = buf.find("还有使用者")
        if poss < 0:
            logger.error("Unknow status when check users\n%s"%buf)
            print "Unknow status when check users\n%s"%buf
            return userstr
        if pose > 0:
##            print buf[poss:pose]
            logger.debug("Found page")
            userstr += buf[poss:pose]
            continue
        elif pose <= 0:
            logger.debug("Scrolled to end page")
            userstr += buf[poss:]
            break
        else:
            logger.error("Unknow status when check users\n%s"%buf)
            return userstr
    tn.write("\b"*len(prefix))
    userstr = clearstr(userstr)
    quitqscr(tn)
    userlist = re.findall("\w+",userstr)
    logger.info("Found %s users"%len(userlist))
    return userlist
def out(msg):
    f = open(filename,"a")
    f.write(msg+"\n")
    f.close()
def queryuser(tn,userid):
    logger.info("Start to query user "+userid)
    if not enterqscr(tn):
        logger.error("Failed to enter user query screen")
        return False
    tn.write(userid[:13]+"\n")
    buf = tn.read_until("其它键继续",TIMEOUT_4)
    res =  re.findall("(\w+) \((.*)\) 上站 .*\n\r上次在 \[(.*)\] 从 \[(.*)\] 访问本站",buf)
    if len(res)==1:
        tn.write(" ")   #quit from user information
        return res[0][3]
    else:
        logger.error("Fairesled to match the user information\n"+buf)
        return buf
def getuserlist(tn):
    prefixs = []
    for c in string.lowercase:
        for c2 in (string.lowercase+string.digits):
            logger.info("Query "+(c+c2))
            users = getusers(tn,c+c2)
            for u in users:
                uinfo=queryuser(tn,u)
                out(u+" "+uinfo)
def filluserinfo(tn):
    with open("userlist.txt") as f:
        data = f.next().strip()
        print data
        return
if __name__ == "__main__":
    filename = "userlist_%s.txt"%time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    tn = login()
    if not tn:
        logger.error("Failed to login")
        exit(1)
    if not gotoboard(tn,"test"):
        logger.error("Failed to go to board test")
        exit(1)
    getuserlist(tn)
##    filluserinfo(tn)
    logout(tn)
