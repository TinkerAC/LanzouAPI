import requests
import re
import random
import json


def parse_lanzouyun_url(url, pwd=None, direct_download=False):
    # Default UserAgent
    UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'

    # Validate url
    if not url:
        return json.dumps({'code': 400, 'msg': '请输入URL'}, ensure_ascii=False, indent=4)

    # Process the URL
    if '.com/' in url:
        url_part = url.split('.com/', 1)[1]
        url = 'https://www.lanzoup.com/' + url_part
    else:
        url = url

    # Get the softInfo
    softInfo = MloocCurlGet(url, UserAgent)

    # Check if '文件取消分享了' in response
    if '文件取消分享了' in softInfo:
        return json.dumps({'code': 400, 'msg': '文件取消分享了'}, ensure_ascii=False, indent=4)

    # Extract softName and softFilesize
    softName = re.findall(r'style="font-size: 30px;text-align: center;padding: 56px 0px 20px 0px;">(.*?)</div>',
                          softInfo)
    if not softName:
        softName = re.findall(r'<div class="n_box_3fn".*?>(.*?)</div>', softInfo)
    softFilesize = re.findall(r'<div class="n_filesize".*?>大小：(.*?)</div>', softInfo)
    if not softFilesize:
        softFilesize = re.findall(r'<span class="p7">文件大小：</span>(.*?)<br>', softInfo)
    if not softName:
        softName = re.findall(r"var filename = '(.*?)';", softInfo)
    if not softName:
        softName = re.findall(r'div class="b"><span>(.*?)</span></div>', softInfo)

    # Check if password is required
    if 'function down_p(){' in softInfo:
        if not pwd:
            return json.dumps({'code': 400, 'msg': '请输入分享密码'}, ensure_ascii=False, indent=4)
        # Extract sign
        segment = re.findall(r"skdklds = '(.*?)';", softInfo)
        if not segment:
            return json.dumps({'code': 400, 'msg': '无法找到签名信息'}, ensure_ascii=False, indent=4)
        post_data = {
            'action': 'downprocess',
            'sign': segment[0],
            'p': pwd
        }
        softInfo = MloocCurlPost(post_data, 'https://www.lanzoup.com/ajaxm.php', url, UserAgent)
        try:
            softInfo_json = json.loads(softInfo)
        except json.JSONDecodeError:
            return json.dumps({'code': 400, 'msg': '解析失败'}, ensure_ascii=False, indent=4)
        softName = [softInfo_json.get('inf', '')]
    else:
        # Not password protected
        link = re.findall(r'\n<iframe.*?name="[\s\S]*?"\ssrc="/(.*?)"', softInfo)
        if not link:
            link = re.findall(r'<iframe.*?name="[\s\S]*?"\ssrc="/(.*?)"', softInfo)
        if link:
            ifurl = 'https://www.lanzoup.com/' + link[0]
            softInfo = MloocCurlGet(ifurl, UserAgent)
            segment = re.findall(r"'sign':'(.*?)'", softInfo)
            if not segment:
                return json.dumps({'code': 400, 'msg': '无法找到签名信息'}, ensure_ascii=False, indent=4)
            post_data = {
                'action': 'downprocess',
                'signs': '?ctdf',
                'sign': segment[0],
            }
            softInfo = MloocCurlPost(post_data, 'https://www.lanzoup.com/ajaxm.php', ifurl, UserAgent)
            try:
                softInfo_json = json.loads(softInfo)
            except json.JSONDecodeError:
                return json.dumps({'code': 400, 'msg': '解析失败'}, ensure_ascii=False, indent=4)
        else:
            return json.dumps({'code': 400, 'msg': '无法找到下载链接'}, ensure_ascii=False, indent=4)

    # Parse softInfo
    if softInfo_json.get('zt') != 1:
        return json.dumps({'code': 400, 'msg': softInfo_json.get('inf', '')}, ensure_ascii=False, indent=4)

    # Construct downUrl1
    downUrl1 = softInfo_json.get('dom', '') + '/file/' + softInfo_json.get('url', '')

    # Get the final download URL
    downUrl2 = MloocCurlHead(downUrl1, 'https://developer.lanzoug.com', UserAgent,
                             'down_ip=1; expires=Sat, 16-Nov-2019 11:42:54 GMT; path=/; domain=.baidupan.com')
    if not downUrl2:
        downUrl = downUrl1
    else:
        downUrl = downUrl2

    if not direct_download:
        result = {
            'code': 200,
            'msg': '解析成功',
            'name': softName[0] if softName else '',
            'filesize': softFilesize[0] if softFilesize else '',
            'downUrl': downUrl
        }
        return json.dumps(result, ensure_ascii=False, indent=4)
    else:
        # Return the download URL
        return downUrl


def Rand_IP():
    arr_1 = ["218", "218", "66", "66", "218", "218", "60", "60", "202", "204", "66", "66", "66", "59", "61", "60",
             "222", "221", "66", "59", "60", "60", "66", "218", "218", "62", "63", "64", "66", "66", "122", "211"]
    ip1id = random.choice(arr_1)
    ip2id = str(random.randint(60, 255))
    ip3id = str(random.randint(60, 255))
    ip4id = str(random.randint(60, 255))
    return f"{ip1id}.{ip2id}.{ip3id}.{ip4id}"


def MloocCurlGet(url, UserAgent=''):
    headers = {
        'X-FORWARDED-FOR': Rand_IP(),
        'CLIENT-IP': Rand_IP(),
    }
    if UserAgent != '':
        headers['User-Agent'] = UserAgent
    else:
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url, headers=headers, verify=False)
    return response.text


def MloocCurlPost(post_data, url, ifurl='', UserAgent=''):
    headers = {
        'X-FORWARDED-FOR': Rand_IP(),
        'CLIENT-IP': Rand_IP(),
        'User-Agent': UserAgent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    if ifurl != '':
        headers['Referer'] = ifurl
    requests.packages.urllib3.disable_warnings()
    response = requests.post(url, data=post_data, headers=headers, verify=False)
    return response.text


def MloocCurlHead(url, guise, UserAgent, cookie):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': UserAgent,
        'Referer': guise,
        'Cookie': cookie,
    }
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    try:
        response = session.get(url, headers=headers, allow_redirects=True, timeout=10, verify=False)
        final_url = response.url
        if final_url != url:
            return final_url
        else:
            return ''
    except requests.exceptions.RequestException:
        return ''
