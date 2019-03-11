#-*- coding:utf-8 -*-
#author:Bolin Chen
import hashlib
import requests
import json
import time
import string
import bs4
from PIL import Image
from urllib3.exceptions import InsecureRequestWarning

#忽略安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
s = requests.Session()
token = ""
root_url = 'https://mp.weixin.qq.com'

data = {
        'name':'',
        'pwd':''
}
headers = {
    'accept-encoding': "gzip, deflate, sdch, br",
    'accept-language': "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
    'accept': "*/*", 'x-requested-with': "XMLHttpRequest", 'connection': "keep-alive",
    'cache-control': "no-cache",
    'referer': 'https://mp.weixin.qq.com/'
}

def trans(str):
        h=hashlib.md5()
        h.update(bytes(str,encoding='utf-8'))
        return h.hexdigest()

#初始化
def before_login():
        s.request("GET", 'https://mp.weixin.qq.com/', headers = headers, verify = False)

#提交账号和密码
def login():
        url = root_url + '/cgi-bin/bizlogin'
        querystring = {"action": "startlogin"}
        payload = "username=" + data['name'] + "&pwd=" + data['pwd'] + "&imgcode=&f=json&token=&lang=zh_CN&ajax=1"
        response = s.request("POST", url, data=payload, headers=headers, params=querystring, verify=False)
        content = response.text
        return json.loads(content)['redirect_url']

#获取二维码
def get_page(redirect_url):
        s.request("GET", redirect_url, headers=headers)
        qr_code = s.get(root_url + '/cgi-bin/loginqrcode?action=getqrcode')
        open('二维码.jpg', 'wb').write(qr_code.content)
        img = Image.open('二维码.jpg')
        img.show()
        
#检查二维码扫描状态
def check_status():
        while True:
                url = root_url + "/cgi-bin/loginqrcode"
                querystring = {"action": "ask", "token": "", "lang": "zh_CN", "f": "json", "ajax": "1"}
                response = s.request("GET", url, headers=headers, params=querystring)
                content = response.text
                if json.loads(content)['user_category'] != 0:
                    break
                time.sleep(1)

#正式登录
def final_login():
        global token
        url = root_url + "/cgi-bin/bizlogin"
        querystring = {"action": "login"}
        payload = "token=&lang=zh_CN&f=json&ajax=1"
        response = s.request("POST", url, data=payload, headers=headers, params=querystring, verify=False)
        content = response.text
        src = json.loads(content)['redirect_url']
        list = src.split("=")
        token = list[3]
        return src

#获取主页
def get_home_page(redirect_url):
        redirect_url = root_url + redirect_url
        response = s.request("GET", redirect_url, headers=headers, verify=False)

#获取当日20条回复
def get_message():
        global token
        src_url = root_url + "/cgi-bin/message?t=message/list&action=&filtertype=0&keyword=&count=100&day=0&filterivrmsg=0&filterspammsg=1&token="+ token +"&lang=zh_CN"
        response = s.request("GET", src_url, headers = headers, verify=False)
        with open('后台回复.txt','w',encoding="utf-8")as f:
                f.write(response.text)
                f.close()
        result_temp = response.text.find("wx.cgiData")
        result_start = response.text.find("list : (",result_temp,len(response.text))
        result_end = response.text.find(").msg_item,",result_start,len(response.text))
        return(response.text[(result_start+8):result_end])

#处理数据
def get_result(str1):
        date = time.strftime("%Y-%m-%d", time.localtime())
        dict = json.loads(str1)
        list = dict['msg_item']
        with open (date+'回复数据.txt','a')as f:
                for each in list:
                        temp_list = each['content'].split("+")
                        if (len(temp_list)==3 and temp_list[0]=='绑定'):
                                f.write("学号："+temp_list[1] + '  ' +"姓名："+ temp_list[2]+'\n')
        end = input('————————————————')


#main
if __name__ == '__main__':
        data['name'] = input("请输入账号：")
        temp_pwd = input("请输入密码：")
        data['pwd'] = trans(temp_pwd)
        before_login()
        redirect_url = root_url + login()
        get_page(redirect_url)
        check_status()
        redirect_url = final_login()
        get_home_page(redirect_url)
        str1 = get_message()
        get_result(str1)
        #以上无BUG
        print('test')
