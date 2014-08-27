#!/usr/bin/env python
#coding=gb2312

###############################################
########## Function list ######################
###############################################
# login()
# gotoboard()
###############################################

import re,sys,os,time,string
import telnetlib
import urllib
import logging
import thread,traceback
server = "122.11.52.86"
userid = "guest"
##password = "1234qwer"
TIMEOUT_0 = 0.1
TIMEOUT_1 = 1
TIMEOUT_2 = 2
TIMEOUT_3 = 3
TIMEOUT_4 = 10
TIMEOUT_5 = 30
TIMEOUT_6 = 60
_keycodes = {
    "up":"\x1b\x5b\x41",                #"\x1B[A",
    "down":"\x1b\x5b\x42",              #"\x1B[B",
    "right":"\x1b\x5b\x43",             #"\x1B[C",
    "left":"\x1b\x5b\x44",              #"\x1B[D",
    "pgup":"\x1b\x5b\x35\x7e",          #"\x1B[5~",
    "pgdn":"\x1b\x5b\x36\x7e",          #"\x1B[6~",
    "end":"\x1b\x5b\x34\x7e",           #"\x1B[4~",
    "home":"\x1b\x5b\x31\x7e",          #"\x1B[1~",
    "ins":"\x1b\x5b\x32\x7e",           #"\x1B[2~",
    "del":"\x1b\x5b\x33\x7e",           #"\x1B[3~",
        
    "F1":"\x1b\x4f\x50",                #"\x1BOP",
    "F2":"\x1b\x4f\x51",                #"\x1BOQ",
    "F3":"\x1b\x4f\x52",                #"\x1BOR",
    "F4":"\x1b\x4f\x53",                #"\x1BOS",
    "F5":"\x1b\x5b\x31\x35\x7e",                #"\x1B[15~",
    "F6":"\x1b\x5b\x31\x37\x7e",                #"\x1B[17~",
    "F7":"\x1b\x5b\x31\x38\x7e",                #"\x1B[18~",
    "F8":"\x1b\x5b\x31\x39\x7e",                #"\x1B[19~",
    "F9":"\x1b\x5b\x32\x30\x7e",                #"\x1B[20~",
    "F10":"\x1b\x5b\x32\x31\x7e",               #"\x1B[21~",
    "F11":"\x1b\x5b\x32\x33\x7e",               #"\x1B[23~",
    "F12":"\x1b\x5b\x32\x34\x7e",               #"\x1B[24~",

    "esc":"\x1B\x1B",           #"\x1b\x1b",
    "tab":"\x09",               #"\x09",
    "enter":"\x0a",             #"\x0a",
    "space":"\x20",             #"\x20",
    "backspace":"\x7f",         #"\x7f",
}
_asciicodes = [
        "\\x1b\\x5b[\\x31-\\x39]*[\\x41-\\x44]",        #*[nA,*[nB,*[nC,*[nD 光标上/下/右/左移n个位置
        "\\x1b\\x5b\\x73",                              #*[s 保存光标位置
        "\\x1b\\x5b\\x75",                              #*[u 恢复光标位置
        "\\x1b\\x5b\\x36\\x6e",                         #*[6n 报告光标位置
        "\\x1b\\x5b[\\x30-\\x39]{1,2}\\x3b[\\x30-\\x39]{1,2}[\\x48\\x66]",      #*[m;nH,*[m;nf 光标移动到绝对坐标(m,n)处
        "\\x1b\\x5b\\x32\\x4a",                                                 #*[2J 清屏,光标移动到(0,0)处
        "\\x1b\\x5b\\x4b",                                                      #*[K 删除从光标处开始到行末的所以字符
        "\\x1b\\x5b[\\x30\\x31\\x34\\x35\\x37]\\x6d",   #*[0m 恢复系统显示背景,前景色
                                                        #*[1m 高亮显示字符
                                                        #*[4m 下划线
                                                        #*[5m 闪烁字符!
                                                        #*[7m 反转显示
        "\\x1b\\x5b\\x33[\\x30-\\x37]\\x6d",    #*[30m ---- *[37m 各种不同的前景色
                                                #       30    Black        31    Red
                                                #       32    Green        33    Yellow
                                                #       34    Blue         35    Magenta
                                                #       36    Cyan         37    White
        "\\x1b\\x5b\\x43[\\x30-\\x37]\\x6d",    #*[40m ---- *[47m 各种不同的背景色
                                                #       40    Black        41    Red
                                                #       42    Green        43    Yellow
                                                #       44    Blue         45    Magenta
                                                #       46    Cyan         47    White
        "\\x1b\\x5b([\\x30-\\x37]{1,2}\\x3b)*[\\x30-\\x37]{0,2}\\x6d",  #*[n1;n2;...;nm
]
###############################################
########### Logging Configuration #############
###############################################
logging.basicConfig( level= logging.INFO,\
                 format= '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                 datefmt= '%a, %d %b %Y %H:%M:%S',\
                 filename= 'myapp.log',\
                 filemode= 'w')

console = logging.StreamHandler()
console.setLevel(logging.WARN)
console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger=logging.getLogger()
##logger.addHandler(console)

###############################################
########### Methods ###########################
###############################################
########Running log to log file################
mylock = thread.allocate_lock()
def out(msg,folderName="",fileName="run.log"):
    localbasedir = os.getcwd()
    mylock.acquire()
    msg=(msg.strip())[:80]
##    padding = 80-len(msg)
##    msg = msg + padding*" "+ "\b"*padding
    sys.stdout.write("\r%-80s\n"%msg)
    sys.stdout.flush()
    timepo = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
    if not type(msg)==str:
        msg = str(msg)
    if folderName == "":
        logfolders = ("")
    else:
        logfolders = ("",folderName)
    for subfolder in logfolders:
        filefolder = os.path.join(localbasedir,subfolder)
        filefullpath = os.path.join(filefolder,fileName)
##        print "filefullpath: ",filefullpath
        if not os.path.exists(filefolder):
            os.makedirs(filefolder)
        f=open(filefullpath,"a")
        f.write(timepo)
        f.write("\t")
        f.write(msg)
        f.write("\r\n")
        f.close()
    mylock.release()
###############################################    
########Running log to console#################
def outconsole(msg):
    mylock.acquire()
##    print len(msg)
##    print msg
    msg = (msg.strip())[:80]
##    padding = 80-len(msg)
##    msg = msg + padding*" " + "\b"*padding
    sys.stdout.write('\r%-80s'%msg)
    sys.stdout.flush()
    #print '\rProcessing:   ', msg, " "*10,"\b"*10,
    mylock.release()
###############################################
######### urllib.urlretrieve download #########
def downloadatt(url,attfilepath,sizeunit="Bytes"):
    logger.debug("Start to download %s to %s"%(url,attfilepath))
##    sys.stdout.write('[')
##    sys.stdout.flush()
    fname,th=urllib.urlretrieve(url,attfilepath,urlcallback)
##    sys.stdout.write(']')
##    sys.stdout.flush()

    actl = eval(th.dict['content-length'])
    if sizeunit=="KB":
        actl = actl/1024
    elif sizeunit=="MB":
        actl = actl/1024/1024
    elif sizeunit=="Bytes":
        pass
    else:
        logger.warning("Unknow attachment size unti %s"%sizeunit)
    logger.debug("Finished download %s %s"%(actl,sizeunit))
    return actl
###############################################
######### urllib.urlretrieve callback #########
def urlcallback(a,b,c):
    """
        call back function
        a,已下载的数据块
        b,数据块的大小
        c,远程文件的大小
    """
    mylock.acquire()
    if c==0:
        prec=0
    else:
        prec=100.0*a*b/c
    if 100 < prec:
        prec=100
    msg = " [%.2f%%]"%prec
    msg = msg + len(msg)*"\b"
    sys.stdout.write('%s'%msg)
    sys.stdout.flush()
    mylock.release()
###############################################
########### Login #############################
def login():
    logger.info("Connecting to "+server)
    tn = telnetlib.Telnet(timeout=TIMEOUT_4)
    try:
        logger.debug('Open server '+server)
        tn.open(server,timeout=TIMEOUT_4)
    except:
        logger.error("Failed to connect")
        logger.debug('Trye to colose Telnet connection and then return')
        tn.close()
        return None
    logger.debug('Wait input user id prompt')
    tmp=tn.read_until("请输入代号:",TIMEOUT_3)
    if not tmp:
        logger.error("No login prompt")
        tn.close()
        return None
    logger.debug('Write user id')
    tn.write(userid+"\n")
##    logger.debug('Wait input password prompt')
##    tmp=tn.read_until("请输入密码:",TIMEOUT_3)
##    if not tmp:
##        logger.error("No password prompt")
##        tn.close()
##        return False
##    logger.debug('Input password '+password)
##    tn.write(password+"\n")

    logger.debug('Wait welcome page')
    result=tn.expect(["密码输入错误",\
                      "你同时上线的窗口数过多，无法再登录",\
                      "错误的使用者代号",\
                      "按任何键继续"
                      ],TIMEOUT_3)
    #print result
    flag = False
    if result[0]==0:
        tn.close()
        logger.error(clearstr(result[2]))
        return None
    elif result[0]==1:
        tn.close()
        logger.error(clearstr(result[2]))
        return None
    elif result[0]==2:
        tn.close()
        logger.error(clearstr(result[2]))
        return None
    elif result[0]==3:
        logger.info("Login successfully")
    elif result[0]==-1:
        logger.warning("No match page found when login")
        flag = True
    else:
        tn.close()
        logger.error(clearstr(result[2]))
        return None
    while result[0]!=5:
        tn.write("\n")
        result=tn.expect(["酸甜苦辣板",
                          "本日十大衷心祝福",
                          "本日十大热门话题",
                          "近期版面事务热点通报",
                          "近期热点",
                          "主选单",
                          "如何处理以上密码输入错误记录",
                          "按任何键继续"
                          ],TIMEOUT_2)

        if result[0]==-1:
            logger.debug(result[1].group())            
            tn.close()
            logger.critical("Unexpect status")
            return None
    logger.info("Current postion is main menu")
    return tn

###############################################
############# Logout ##########################
def logout(tn):
    logger.info("Logout from server")
    tn.close()
###############################################
############# read buffer #####################
def read_all(tn,timeout=TIMEOUT_3):
    if timeout>0:
        time.sleep(timeout)
    res = tn.read_very_eager()
    return clearstr(res)
###############################################
################ Go to board ##################        
def read_scr_update(tn):
    """
    This method is designed to capture all returned data from sever when useroperating
    but not includes the post read mode
    """
    time.sleep(1)
    logger.debug("Read board updated content")
    #if ends with a cursor reloacting
    #*[4-23;2H, each response of board update will end with re-locating the cursor posstion
    relocator=re.compile("\\x1b\\x5b(?:[\\x34-\\x39]|\\x31[\\x30-\\x39]|\\x32[\\30-\\x33])\\x3b\\x32\\x48$") 
    #if ends with "其它键继续*[m"
    #the end of user information pageS
    restorer=re.compile("其它键继续\\x1b\\x5b\\x6d$") 
    #if ends with "*[nAB\r?
    #the end of move cursor
    movecursor = re.compile("\\x1b\\x5b[\\x31-\\x39]+[\\x41-\\x42]\r?$")  
    res=tn.expect([relocator,restorer,movecursor],TIMEOUT_4)
    time.sleep(1)
    lmsg = tn.read_very_eager()
    if len(lmsg)>0:
        logger.warning("Unreached all buffer when read page")
        logger.debug("\nRreached:\n"+"*"*100+"\n"+res[2])
        logger.debug("\nUnreached:\n"+"*"*100+"\n"+lmsg)
    if res[0]>=0:
        log = clearstr(res[2])
##        print "#"*100
##        print log
        return log
    elif res[0]==-1:
        logger.error("Does't match the reg expr when read_scr_update()\n"+res[2])
        return clearstr(res[2])
    else:
        logger.critical("Abnormal status in read_scr_update()")
        logger.info(clearstr(res))
        raise Exception,"Abnormal status in read_scr_update()"
###############################################
# Refresh board actively by press s and enter #
def udpate_board(tn):
    """line is the former position"""
    logger.debug("Refresh board and clear unread flag")
    tn.write("s")
    tmp=tn.read_until("请输入讨论区名称",TIMEOUT_2)
    if not re.search("请输入讨论区名称",tmp):
        #print "tmp:",tmp
        logger.warning("Failed to refresh board")
        return False
    tn.write("\n")
    #Return after the cursor returned to former place
    logger.debug("Refreshed succeefully")
##    return res
###############################################
############# redwaw the screen ###############
def read_board(tn):
    res = tn.expect(['停留\[\s{1,2}\d{1,3}:\s{0,2}\d{1,2}\]'],TIMEOUT_4)
    if res[0]==-1:
        logger.warning("Failed in read_board(停留\[\s{0,2}\d{1,2}:\s{0,2}\d{1,2}\])\n%s"%res[2])
    return clearstr(res[2])
###############################################
############# redwaw the screen ###############
def read_board_update(tn,pid=None):
    flag = True
    if type(pid)==int and pid>0:
        line = pid%20
        line = line==0 and "(23|4)" or line+3
    else:
        line = "\d+"
    res = tn.expect(["\\x1b\[%s;2H"%line],TIMEOUT_4)
    if res[0]==-1:
        logger.warning("Failed in read_board_update(pid=%s,line=%s)\n%s"%(pid,line,res[2]))
        if logging.getLogger().getEffectiveLevel()==logging.DEBUG:
            redrawcurscreen(tn)
            buf = read_board(tn)
            logger.debug("Full screen\n%s"%buf)
        flag = False
    return flag,clearstr(res[2])
###############################################
############# redwaw the screen ###############
def redrawcurscreen(tn):
    logger.debug("Start to redraw current screen by CTRL-L")
##    read_all(tn,timeout=TIMEOUT_1)
##    logger.debug("Cleared the buffer")
##    logger.debug("Redraw the screen")
    tn.write("\f")
    return True
###############################################
############# string to hex ###################
def a2hex(s):
    r=[hex(ord(x)) for x in s]
    return string.join(r,"\\x")
###############################################
############# clear string ####################
def clearstr(oristr):
    res = re.sub("\\x1b\\x5b[\\x30-\\x39]+[\\x41-\\x44]"," ",oristr)    #上下左右键移动标志先移除，否则在版面主界面中，会导致用户id与日期连接
    res = re.sub("\\x1b\[[0-9]{1,2};[0-9]{1,2}[Hf]","\n\r   ",res)                  #*]4;2H 这标志为版面左上角重定位标志
    
    ex=string.join(_asciicodes,"|")
    res = re.sub(ex,"",res)
    return res
###############################################
############# multiple function menu ##########
def mulfunread(tn,num,para):
    menu = ["文摘模式","主题模式","精华模式","原作模式","作者模式","标题模式","","",""]
            
    logger.info("Go multiple function page")
    tn.write("\a")
    tn.read_until("切换模式到:",TIMEOUT_4)
    tn.write(num+"\n")

###############################################
############# goto a board ####################
def gotopost(tn,postid):
    logger.debug("Go to post %s"%postid)
    tn.write('%s\n'%postid)
    if type(postid)==str:
        postid = eval(postid)
    if type(postid)==int and postid>0:
        line = postid%20
        line = line==0 and 23 or line+3
    res = tn.expect([">","\\x1b\[%s;2H"%line],TIMEOUT_4)
    if res[0]==-1:
##        redrawcurscreen(tn)
##        buf = read_all(tn)
##        logger.warning("Failed to go to post %s\nReturned content:%s\nCurrent screen%s"%(postid,res[2],buf))
        logger.warning("Failed to go to post %s\nReturned content:%s"%(postid,res[2]))
        return False
    return True
###############################################
############# goto a board ####################
def gotoboard(tn,boardname):
    logger.info("Go to board "+boardname)
    flag = 20
    tn.write("s")
    while True:
        flag -= 1
        if flag==0:
           logger.error("Failed to swithc board to "+boardname+", can't get the board name input prompt")
           return False
        res=tn.expect(["请输入讨论区名称",
                       "\\xa1\\xf4\\x53\\x29",  #◆S)
                       "\\xa1\\xf4\\x47\\x29"], #◆G)
                      TIMEOUT_4)
        if res[0] == 0:
            logger.debug("Got input prompt")
            break
        elif res[0] == 1:
            logger.debug("◆S)")
            tn.write("\n")
        elif res[0] == 2:
            logger.debug("◆G)")
            tn.write("s")
        elif res[0] == -1:
            logger.debug("No input prompt")
            tn.write(_keycodes["left"])
        else:
            logger.critical("Abnormal status")
            return False
    tn.write(boardname)
    tn.write("\n")
    while True:
        result=tn.expect(["错误的讨论区名称","按任何键继续",re.compile("\[%s.*\]"%boardname,re.I)],TIMEOUT_4)
        if result[0]==0:
            tn.write("\n")
            logger.warning(clearstr(result[1].group()))
            return False
        elif result[0]==1:
            logger.debug("进版画面")
            tn.write("\n")
        elif result[0]==2:
            logger.debug("Enterred board %s successfully"%result[1].group())
            return result[1].group()
        else:
            logger.debug("Failed to enter board "+boardname)
            logger.info(result[2])
            return False
###############################################
################ Extract posts from string ####  
def extractnewposts(scr):
    logger.debug("Extract posts")
    #0: cursor
    #1: post id
    #2: spark
    #3: user id
    #4: month and day
    #5: title
    
    ps=re.findall("(.?)\s+(\d+)\s+([\*mbg\s])\s+(\w+)\s+((?:\w\w\w)?\s*\d*\.?)\s*(@?(?:Re:|\\xa1\\xf1) .*)",scr)   #for cleared str
##    x=[p[1] for p in ps]
##    logger.debug("Found %d posts"%len(ps))
##    logger.debug(x)
##    x = [t[5] for t in ps if t[5].find("版主")>=0]
##    if len(x)>0:
##        logger.error("extractnewposts error\n"+scr)
##        exit(1)
    return ps
############## read and analyze a post ########  
def readpost(tn,boardname,post):
    """
    suppose current page is the board page
    """
    logger.debug("Start to read post")
    if post[2]=='*':
        tn.write('c')
    if not post[5].startswith('@'):
        return False
    logger.debug("Found post attachment")
    read_all(tn,timeout=1)
    logger.debug("Cleared the buffer")
    tn.write('\n')
    postcontent = ""
    while True:
        res=tn.expect(["下面还有喔 \(\d{1,2}%\) 第\((\d+)-(\d+)\)行","下面还有喔 \(\d{3}%\) 第\((\d+)-(\d+)\)行","\[阅读文章\].*\^X或p"],TIMEOUT_2)
        if res[0]==0:
            logger.debug(res[1].group())
            postcontent+=res[2][:-len(res[1].group())]
            tn.write("g")
            tn.read_until("跳转到的行号:",TIMEOUT_2)
            nextlinenumber = str(eval(res[1].group(2)))
            tn.write(nextlinenumber+"\n")
        elif res[0]>=1:
            logger.debug(res[1].group())
            postcontent+=res[2]
            break
        else:
            redrawcurscreen(tn)
            tn = read_all(tn)
            logger.warning("Abnormal status when readpost\nCurrent screen:\n%s"%buf)
            return False
    while True:
        #print redrawcurscreen()
        tn.write('q')
        res=tn.expect(['\[阅读文章\]','停留\[\s+\d{1,2}:\d{1,2}\]'],TIMEOUT_2)
        if res[0]==0:
            logger.debug("Read to end")
            continue
        elif res[0]==1:
            logger.debug("Returned from post page")
            break
        else:
            logger.warning("Abnormal status when return from post page")
            print res[2]
            return False
    pid = post[1]
    userid = post[3]
    title = post[5]
    
    title=re.sub('[\\\/:\*\?"<>|]','',title)
    filename="%s_%s_%s.txt"%(pid,userid,title)
    userfolder = os.path.join(boardname,post[3])
    if not os.path.exists(userfolder):
        os.makedirs(userfolder)
    posttxtfile = os.path.join(userfolder,filename)

    if os.path.exists(posttxtfile):
        logger.debug("Topic file %s already existed"%posttxtfile)
    else:
        try:
            f = open(posttxtfile,'w')
            f.write(clearstr(postcontent))
            f.close()
            logger.debug("Generated "+posttxtfile)
        except IOError:
            logger.warning("Invalid file name: "+filename)
            title = "Invalid file name"
            filename="%s_%s_%s.txt"%(pid,userid,title)
            posttxtfile = os.path.join(userfolder,filename)
            f = open(posttxtfile,'w')
            f.write(clearstr(postcontent))
            f.close()
            logger.debug("Generated "+posttxtfile)
    atts = re.findall("附[^:]+: (.*) \((\d+) (\w+)\) (?:链接:?)?(?:\\x1b\[K)?\n\r.*\\x1b\[4m(http://att\.newsmth\.net/att\.php\?.+)[\\x1b|\n]",postcontent)
    if len(atts)==0:
                logger.error("No attachement mactched\nCurrent post:%s\n%s\nCurrent Screen:%s"%(string.join(post," "),"#"*100,postcontent))
                return
    for name,size,unit,url in atts:
        attfilename="%s_%s_%s_%s"%(pid,userid,title,name)
        attfilepath = os.path.join(userfolder,attfilename)
        if os.path.exists(attfilepath):
            logger.debug("Attchment file %s already exists"%attfilepath)
            continue
        logmsg = "%-13s%s"%(boardname,attfilename)
        logmsg = logmsg.strip()
        outconsole(logmsg)
        if downloadatt(url,attfilepath,unit)==eval(size) or\
            downloadatt(url,attfilepath,unit)==eval(size) or\
            downloadatt(url,attfilepath,unit)==eval(size):
            logger.debug("Generated "+attfilepath)
            out(logmsg,boardname)
        else:
            out("Failed to download "+attfilepath,boardname)
            logger.error("Attachment %s %s downloaded failed. act/exp = %s/%s"%(boardname,attfilename,0,size))
##        outconsole(logmsg)

    return True

###############################################
################ board thread ##################  
def boardhandler(tn,boardname,startPos=-1):
    boardname = gotoboard(tn,boardname)
    if not boardname:
        return
    buf=read_board_update(tn)[1]

    if startPos>0:
        if not gotopost(tn,startPos):
            return
        buf = read_board_update(tn,startPos)[1]
        logger.debug("\n"+buf)
        redrawcurscreen(tn)
        buf = read_board(tn)
        
    ps = extractnewposts(buf)
    flag = startPos
    pgdnflag = True
    while True:
        if len(ps)==0:
            logger.debug("flag position: %s"%flag)
            if flag%20 == 0 and pgdnflag:
                logger.debug("page down")
                tn.write(" ")   #page down
                read_board_update(tn,1)
                pgdnflag = False
            else:
                logger.debug("refresh board")
                tn.write("f")   #update current page
                ff = read_board_update(tn,flag)[0]
                if not ff:
                    logger.info("Posts deleted when fresh page")
                    flag = -1
            redrawcurscreen(tn)
            buf = read_board(tn)
            logger.debug("\n"+buf)
            tmp=extractnewposts(buf)
            ps = [x for x in tmp if eval(x[1]) > flag]
            if len(tmp)==0 or len(ps)==0:
                time.sleep(TIMEOUT_4)
            continue
                
##            tmp1 = [x for x in tmp if eval(x[1]) == flag]
##            tmp2 = [x for x in tmp if eval(x[1]) > flag]
            
##            if len(tmp2)==0 and len(tmp1) > 0:
##                time.sleep(TIMEOUT_5)
##                continue
##            elif len(tmp2)==0 and len(tmp1) == 0:
##                #Now post deleted and in one of last pages
##                logger.debug("post deleted, and now screen is \n"+buf)
##                ps = tmp
##            elif len(tmp2)>0:
##                ps = tmp2
##                logger.debug("New posts found: %s"%[x[1] for x in ps])
##            else:
##                logger.error("Unknow status when checking new posts\n"+buf)
        pgdnflag = True
        p=ps.pop(0)
        logger.debug("Work on post %s"%(string.join(p," ")))
        outconsole("Processing: %-13s%-8s%-13s%s"%(boardname,p[1],p[3],p[5]))
        if not gotopost(tn,p[1]):
            flag = -1
            ps = []
            continue
        readpost(tn,boardname,p)
        flag =  eval(p[1])
        
def boardthread(boardname,startPos=0):
    while True:
        try:
            tn = login()
            if tn:
                boardhandler(tn,boardname,startPos)
        except:
            msg = traceback.format_exc()
            logger.critical(msg)
        finally:
            if tn:
                logout(tn)
        time.sleep(TIMEOUT_6)
if __name__=="__main__":
    boardnames = {"familylife":0}#,"Picture":601}#"Myphoto":9269}##
    for bdn in boardnames:
        pid = thread.start_new_thread(boardthread,(bdn,boardnames[bdn]))
        print bdn,pid
    while 1:
        time.sleep(1000)
