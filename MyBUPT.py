
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import requests
from bs4 import BeautifulSoup
from idna import unicode

url = 'https://bbs.byr.cn/user/ajax_login.json'
my_header = {'x-requested-with':'XMLHttpRequest'}
byr_data = {'id':'sanlaoye','passwd':'*******'}

s = requests.Session()   #二次请求会话
r = s.post(url,data = byr_data,headers = my_header)   #网站登录
# print (r.text)
def getHtml(page):
    for index in range(page):      #爬取多页内容
        hot_url='https://bbs.byr.cn/board/ParttimeJob?p='+str(index)+'&_uid=sanlaoye'
        hot = s.get(hot_url,headers = my_header)
        html2=hot.content
        if index==0:
            html=html2
        else:
            html=html+html2
    return html

def parse(html):
    lj=BeautifulSoup(html,'html.parser') #使用美丽汤进行解析
    job=lj.find_all('td','title_9') #寻找目标所在的标签
    colt=[]
    for rec in job:
        totalJob=rec.a.string
        colt.append(totalJob)


    job=lj.find_all('td','title_9')
    colt=[]
    webColt=[]
    for rec in job:
        totalJob=rec.a.string
        totalWeb=rec.a.attrs['href']
        colt.append(totalJob)
        webColt.append('https://bbs.byr.cn'+totalWeb)


    T=lj.find_all('td','title_10')
    if T:
        Tcolt=[]
        p=0
        for rec in T:
            if p%2==0:
                totalDate=rec.string
                Tcolt.append(totalDate)
            p=p+1
    else:
        print("这里有异常啊")

    ZYF=pd.DataFrame({'发布时间':Tcolt,'岗位名称':colt,'链接':webColt})#利用pandas构建数据表
    return ZYF

def sendmail(subject, msg, toaddrs, fromaddr, smtpaddr, password):
    ''''' 
    @subject:邮件主题 
    @msg:邮件内容 
    @toaddrs:收信人的邮箱地址 
    @fromaddr:发信人的邮箱地址 
    @smtpaddr:smtp服务地址，可以在邮箱看，比如163邮箱为smtp.163.com 
    @password:发信人的邮箱密码 
    '''
    mail_msg = MIMEMultipart()
    if not isinstance(subject, unicode):
        subject = unicode(subject, 'utf-8')
    mail_msg['Subject'] = subject
    mail_msg['From'] = fromaddr
    mail_msg['To'] = ','.join(toaddrs)
    mail_msg.attach(MIMEText(msg, 'html', 'utf-8'))
    try:
        s = smtplib.SMTP()
        s.connect(smtpaddr)  # 连接smtp服务器
        s.login(fromaddr, password)  # 登录邮箱
        s.sendmail(fromaddr, toaddrs, mail_msg.as_string())  # 发送邮件
        s.quit()
    except Exception as e:
        print("Error: unable to send email")
        print(traceback.format_exc())

chtml=getHtml(5)
inf=parse(chtml)

f = str(inf[1:])
fromaddr = "thefinalwinner@sina.com"  #你要使用的源邮箱地址
smtpaddr = "smtp.sina.com"
toaddrs = ["thefinalwinner@sina.com"] #你要发送的目的邮箱地址
subject = "测试邮件"
password = "*******"#输入你自己的邮箱密码
msg = f
sendmail(subject, msg, toaddrs, fromaddr, smtpaddr, password) #发送指令
