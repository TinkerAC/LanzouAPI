# LanzouAPI

Python 版本的蓝奏盘直连解析工具。它支持接受分享链接和可选的提取码，并返回文件的下载直链。

## 感谢
本仓库翻译自 [hanximeng/LanzouAPI](https://github.com/hanximeng/LanzouAPI)，感谢前辈的付出。

## 快速上手

### 含提取码示例
```python
url = "分享链接"
pwd = "提取码"
download_link = parse_lanzouyun_url(url=url, pwd=pwd)
print(download_link)
```



### 不含提取码

```python
download_link = parse_lanzouyun_url(url=url)
```


### 输出结果
```json
{
    "code": 200,
    "msg": "解析成功",
    "name": "S.ZS.zip",
    "filesize": "35.4 M",
    "downUrl": "https://c1029.lanosso.com/107a87c757b8b64f4f0bae79c7f583cc/66e3c77a/2020/12/28/743c9b1174f379eb14674089c9b17db2.zip?fn=S.ZS.zip"
}
```
