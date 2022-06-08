#!/usr/bin/python3
from requests import post, get
from time import time
from ast import literal_eval as le  ## String转化为List或Dictionary
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning as w
disable_warnings(w) ## 屏蔽无SSL验证的警告

############### 手动输入一下内容 ##################
USER = ''        ## 用户名 (手机号/邮箱)
PASSWORD = ''    ## 密码
#################################################

def btbar_login(BTBASESSID): ## 实际上可用旧cookie登录，但有效期太短（少于半天？），因此将一律重新登录（传参'now'）
	url = 'https://u.aibtba.com/user/login'
	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
		"Origin": "https://u.aibtba.com",
		"Accept-Encoding": "gzip, deflate, br",
		"Connection": "keep-alive",
		"Accept": "*/*",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
		"Referer": "https://u.aibtba.com/user/login",
		"Content-Length": "58",
		"Accept-Language": "zh-CN,zh-Hans;q=0.9"
	}

	if BTBASESSID != 'now':
		time_stamp = str(int(time()))
		cookieText = 'BTBASESSID=' + BTBASESSID + '; Hm_lpvt_19a24d91cbe5649b8e7449e1b7c1a97e=' + time_stamp + '; Hm_lvt_19a24d91cbe5649b8e7449e1b7c1a97e=' + time_stamp
		headers['Cookie'] = cookieText
	if USER:
		data = {
			'mobile_email': USER,
			'bt_password': PASSWORD,
			'submit': '1'
		}
	else:
		quit()
	response = post(url=url, headers=headers, data=data, verify=False)
	return response

def btbar_checkin(cookie, coin):
	url_0 = 'https://u.aibtba.com/sign?search_referer=https%3A%2F%2Fu.aibtba.com%2F&callback=Json'
	url = 'https://u.aibtba.com/sign/select?callback=Json'
	time_stamp = str(int(time()))
	cookieText = cookie + 'Hm_lpvt_19a24d91cbe5649b8e7449e1b7c1a97e=' + time_stamp + '; Hm_lvt_19a24d91cbe5649b8e7449e1b7c1a97e='+ time_stamp + '; search_referer=https%253A%252F%252Fu.aibtba.com%252F'
	## Hm_lpvt.. 当前时间戳; Hm_lvt.. 猜测是曾经登录时间（可多个，形如1654364167,1654364158）
	headers_0 = {
		"Accept": "*/*",
		"Connection": "keep-alive",
		"Referer": "https://www.aibtba.com/",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "zh-CN,zh-Hans;q=0.9",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
		"Cookie": cookieText
	}
	response_0 = get(url=url_0, headers=headers_0, verify=False)  ## 点击签到
	addCoin = le(response_0._content.decode('unicode_escape').replace('Json(', '').replace(')', ''))[1].replace('获得','').replace('BT币', '')
	## 签到获取的BT币（当日首次签到可截取）：首先将返回信息从bytes形式解码为汉字，再列表化，列表的第二项为获取BT币的信息，最后去除无关文字后，并整形化
	if addCoin == '已签到':  ## 重复登录
		addCoin = 0
	coin += int(addCoin)
	headers = headers_0
	headers['Cookie'] = cookieText + '; bt_gold=' + str(coin) + '; bt_sign=%25E5%25B7%25B2%25E7%25AD%25BE%25E5%2588%25B0' ## bt_sign二次URL解码 -> 已签到
	response = get(url=url, headers=headers, verify=False)  ## 获取签到信息
	return response

def check_status(code):
	status = 'Error'
	if code == 200:
		status = 'OK'
	return status

## 从返回的类成员 cookies 中获取 BTBASESSID、bt_gold、bt_nickname、bt_user_id
loginAction = btbar_login('now')
loginResult = { 'status': loginAction.status_code, 'cookies': loginAction.cookies }
cookiesList = str(loginResult['cookies']).split()

try:
	cookies = ''
	for e in cookiesList:
		if '=' in e:
			cookies = cookies + e + '; '
			if 'bt_gold' in e:
				coin = int(e.replace('bt_gold=', ''))
	print('登录结果：', check_status(loginResult['status']), '\n账号Cookie：', cookies, end='\n\n')
except Exception as ex:
	print(ex)
	quit()

if not cookies:
	quit()

checkinAction = btbar_checkin(cookies, coin)
# checkinResult = checkinAction.__dict__  ## 类成员遍历
# for key in checkinResult:
# 	print(key + ': ' + str(checkinResult[key]))

try:
	checkinResult = { 'status': checkinAction.status_code, 'result': le(checkinAction._content.decode('unicode_escape').replace('Json(', '').replace(')', '')) }
	print('签到结果：', check_status(checkinResult['status']) + '，', end='')
except Exception as ex:
	print(ex)
	quit()

for key, value in checkinResult['result']['date'].items():
	if value == '':
		if key == '今天':
			print('今日获得' + str(checkinResult['result']['count']) + 'BT币', '\n\n预计可得BT币：')
		continue
	else:
		print('  ' + key.replace('.', '月') + '日 -', value)

