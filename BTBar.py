################ 手动输入以下内容 ##################
## 用户名 (手机号/邮箱)
USER = ''

## 密码
PASSWORD = ''

## 曾经登录的时间戳（若连续登录则取第一天）；
## 无内容则提交当前登录时间；
## 可自定义（在输出结果中提取，或自行抓取“Hm_lvt”字样的cookie）
PastLoginTime = ''
#################################################

from requests import post, get
from time import time
from re import sub                     ## 正则替换
from ast import literal_eval as le     ## String转化为List或Dictionary
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning as w
disable_warnings(w)                    ## 屏蔽无SSL验证的警告

HEADERS = {
	"Accept": "*/*",
	"Connection": "keep-alive",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zh-Hans;q=0.9",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"  ## macOS Safari，较Chrome所需头部信息少
}
SEARCH_REFERER = 'search_referer=https%253A%252F%252Fu.aibtba.com%252F'  ## search_referer二次URL解码 -> https://u.aibtba.com/
BT_SIGN = 'bt_sign=%25E5%25B7%25B2%25E7%25AD%25BE%25E5%2588%25B0'        ## bt_sign二次URL解码 -> 已签到  

def btbar_login(BTBASESSID): 
## 实际上可用旧cookie登录，但有效期太短，目前一律重新登录（传参'now'）
	if not USER or not PASSWORD: 
		print('请正确输入用户信息。')
		quit()
	url = 'https://u.aibtba.com/user/login'
	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
		"Origin": "https://u.aibtba.com",
		"Referer": "https://u.aibtba.com/user/login",
		"Content-Length": "58"
	}
	headers.update(HEADERS)

	if BTBASESSID != 'now':
		time_stamp, pastTime = get_time_stamp()
		cookieText = f'BTBASESSID={BTBASESSID}; Hm_lpvt_19a24d91cbe5649b8e7449e1b7c1a97e={time_stamp}; Hm_lvt_19a24d91cbe5649b8e7449e1b7c1a97e={pastTime}'
		headers['Cookie'] = cookieText
		
	data = {
		'mobile_email': USER,
		'bt_password': PASSWORD,
		'submit': '1'
	}
	response = post(url=url, headers=headers, data=data, verify=False)
	print('当前登录时间戳:', int(time()))
	return response

def btbar_checkin(cookie, coin):
	url_0 = 'https://u.aibtba.com/sign?search_referer=https%3A%2F%2Fu.aibtba.com%2F&callback=Json'
	url = 'https://u.aibtba.com/sign/select?callback=Json'
	time_stamp, pastTime = get_time_stamp()
	cookieText = f'Hm_lpvt_19a24d91cbe5649b8e7449e1b7c1a97e={time_stamp}; Hm_lvt_19a24d91cbe5649b8e7449e1b7c1a97e={pastTime}; {cookie}{SEARCH_REFERER}'
	## Hm_lpvt.. 当前时间戳; Hm_lvt.. 猜测是曾经登录时间（可多个，形如1654364167,1654364158）
	headers_0 = {
		"Referer": "https://www.aibtba.com/",
		"Cookie": cookieText
	}
	headers_0.update(HEADERS)
	response_0 = get(url=url_0, headers=headers_0, verify=False)  ## 点击签到

	addCoin = le(sub(r'Json\(|\)', '', response_0._content.decode('unicode_escape')))[2]
	## 签到获取的BT币（当日首次签到可截取）：首先将返回信息从bytes形式解码为汉字，替换无关字符后列表化（literal_eval），列表的第三项为获取的BT币数
	coin += addCoin

	headers = headers_0
	headers['Cookie'] = sub(r'bt_gold=\d{1,4}', f'bt_gold={coin}', cookieText) + f'; {BT_SIGN}'
	response = get(url=url, headers=headers, verify=False)  ## 获取签到信息
	return response, addCoin, coin   ## addCoin作为是否 重复签到 的判定（获得0BT币）

#def refresh(cookieText, nowCoin):
#	url = 'https://www.aibtba.com'
#	headers = HEADERS
#	headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
#	time_stamp, pastTime = get_time_stamp()
#	cookieText = sub(r'bt_gold=\d{1,4}', 'bt_gold=' + str(nowCoin), cookieText)
#	headers['Cookie'] = f'Hm_lpvt_19a24d91cbe5649b8e7449e1b7c1a97e={time_stamp}; Hm_lvt_19a24d91cbe5649b8e7449e1b7c1a97e={pastTime}; {cookieText}; {BT_SIGN}; {SEARCH_REFERER}'
#	response = get(url=url, headers=headers, verify=False)
#	try: 
#		if response.status_code != 200:
#			print('\n', '刷新出错了（不影响币值）。')
#	except Exception as ex:
#		print(ex)

def get_time_stamp():
	time_stamp = str(int(time()))
	pastTime = str(PastLoginTime)
	if not pastTime.strip():
		pastTime = time_stamp
	return time_stamp, pastTime

def check_status(code):
	status = 'Error'
	if code == 200: status = 'OK'
	return status

## 从返回的类成员 cookies 中获取 BTBASESSID、bt_gold、bt_nickname、bt_user_id
loginAction = btbar_login('now')

try:
	loginResult = { 'status': loginAction.status_code, 'cookies': loginAction.cookies }
	cookiesList = str(loginResult['cookies']).split()
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

if not cookies: quit()

checkinAction, checkinJudge, coin = btbar_checkin(cookies, coin)
# checkinResult = checkinAction.__dict__  ## 类成员遍历
# for key in checkinResult:
# 	print(key + ': ' + str(checkinResult[key]))

try:
	checkinResult = { 'status': checkinAction.status_code, 'result': le(sub(r'Json\(|\)', '', checkinAction._content.decode('unicode_escape'))) }
	keepCheckin = checkinResult['result']['count']
	print('签到结果：', check_status(checkinResult['status']) + '，已连续签到'+ str(keepCheckin) + '天，', end='')
	if not checkinJudge: 
		print('请勿重复签到，', end='')
	if keepCheckin >= 7:               ## 今日获得的BT币 -> 连续签到少于7天，获得数=连续签到数；连续签到多于7天，获得数=7
		keepCheckin = 7
except Exception as ex:
	print(ex)
	quit()

for key, value in checkinResult['result']['date'].items():
	if value == '':
		if key == '今天':
			print(f'今日获得{keepCheckin}BT币，目前一共{coin}BT币', '\n\n预计可得BT币：')
		continue
	else:
		print('  ' + key.replace('.', '月') + '日 -', value)

# refresh(cookies, coin)    ## 刷新

