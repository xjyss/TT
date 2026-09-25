# coding=utf-8
#!/usr/bin/python
import sys
import requests
import re
import json
from base64 import b64decode
from urllib.parse import urljoin, unquote
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.host = "https://ajxjeb785dhjw.3p.christmas"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        print(f"二区: {self.host}")

    def _double_decode_html(self, raw_html):
        try:
            match = re.search(r'var str\s*=\s*[\'\"](.*?)[\'\"];', raw_html, re.S)
            if match:
                cipher = match.group(1)
                s1 = b64decode(cipher)
                s2 = b64decode(s1)
                return s2.decode("utf-8")
        except Exception:
            pass
        return raw_html

    def getName(self):
        return "二区"

    def isVideoFormat(self, url):

        if not url: return False
        url_lower = url.lower()
        if '.html' in url_lower: return False 
        return '.m3u8' in url_lower or '.mp4' in url_lower

    def manualVideoCheck(self):
        return False

    def _decrypt_title(self, encrypted_text):
        try:
            if not encrypted_text: return ""
            decrypted_chars = []
            for char in encrypted_text:
                decrypted_chars.append(chr(ord(char) ^ 128))
            result = ''.join(decrypted_chars)

            if sum(1 for c in result if ord(c) < 32 and c not in '\t\n\r') > len(result) * 0.3:
                return encrypted_text
            return result
        except:
            return encrypted_text

    def _extractVideoItems(self, html_content):
        vods = []
        try:
            # 兼容多种列表模板
            items = re.findall(r'<li[^>]*class="content-item"[^>].*<a[^>]*href="([^"]+)"[^>]*>.*?<img[^>]*data-original="([^"]+)"[^>]*>.*?<p[^>]*class="text-ellipsis[^"]*"[^>]*>(.*?)</p>', html_content, re.S)
            if not items:
                items = re.findall(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]+)"', html_content, re.S)

            for href, img, title_raw in items:
                title = self._decrypt_title(title_raw.strip())
                if not title: title = title_raw.strip()
                
                # 补全链接
                vid_url = href if href.startswith('http') else urljoin(self.host, href)
                pic_url = img if img.startswith('http') else urljoin(self.host, img)
                
                vods.append({
                    'vod_id': vid_url,
                    'vod_name': title,
                    'vod_pic': pic_url,
                    'vod_remarks': ''
                })
        except Exception as e:
            print(f"List parsing error: {e}")
        return vods

    def homeContent(self, filter):
        result = {}
        classes = [
             {'type_name': '全部','type_id': '/index.php/vod/type/id/3.html'},
             {'type_name': '推荐','type_id': '/index.php/vod/type/id/4.html'},
             {'type_name': '动漫','type_id': '/index.php/vod/type/id/5.html'},
             {'type_name': '黑料','type_id': '/index.php/vod/type/id/6.html'},
             {'type_name': '无码','type_id': '/index.php/vod/type/id/56.html'},
             {'type_name': '字幕','type_id': '/index.php/vod/type/id/7.html'},
             {'type_name': '欧美','type_id': '/index.php/vod/type/id/8.html'},
             {'type_name': '传媒','type_id': '/index.php/vod/type/id/10.html'},
             {'type_name': '网黄','type_id': '/index.php/vod/type/id/55.html'},
             {'type_name': 'JK','type_id': '/index.php/vod/type/id/57.html'},
             {'type_name': '国产','type_id': '/index.php/vod/type/id/54.html'},
             {'type_name': '热门','type_id': '/index.php/vod/type/id/5.html'},

        ]
        result['class'] = classes
        try:
            res = requests.get(self.host, headers=self.headers, timeout=5)
            result['list'] = self._extractVideoItems(res.text)
        except:
            result['list'] = []
        return result

    def homeVideoContent(self):
        return self.homeContent(False)

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        pg = int(pg) if pg else 1
        url = tid if tid.startswith('http') else urljoin(self.host, tid)
        if pg > 1:
            url = url.replace('.html', f'/page/{pg}.html') if url.endswith('.html') else f"{url}/page/{pg}.html"
        
        try:
            res = requests.get(url, headers=self.headers, timeout=120)
            res.encoding = 'utf-8'
            vods = self._extractVideoItems(res.text)
            result['list'] = vods
            result['page'] = pg
            result['pagecount'] = pg + 1 if len(vods) > 0 else pg
            result['limit'] = 20
            result['total'] = 9999
        except:
            result['list'] = []
        return result

    def detailContent(self, ids):
        vid = ids[0]
        url = vid if vid.startswith('http') else urljoin(self.host, vid)
        vod = {
            'vod_id': vid,
            'vod_name': '',
            'vod_pic': '',
            'vod_remarks': '',
            'vod_content': ''
        }
        
        try:
            res = requests.get(url, headers=self.headers, timeout=120)
            res.encoding = 'utf-8'
            html = res.text
            
            t_match = re.search(r'<h1[^>]*>(.*?)</h1>', html) or re.search(r'<title>(.*?)</title>', html)
            if t_match:
                raw_title = t_match.group(1).split('-')[0].strip()
                decrypted = self._decrypt_title(raw_title)
                vod['vod_name'] = decrypted if len(decrypted) > 1 else raw_title

            img_match = re.search(r'class="(?:poster|dyimg)"[^>]*src="([^"]+)"', html)
            if img_match:
                vod['vod_pic'] = img_match.group(1) if img_match.group(1).startswith('http') else urljoin(self.host, img_match.group(1))

            vod['vod_play_from'] = '二区线路'
            vod['vod_play_url'] = f'立即播放${url}'
            
        except Exception as e:
            print(f"Detail error: {e}")
            
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):

        url = id
        headers = self.headers.copy()
        headers['Referer'] = url 
        
        try:

            if self.isVideoFormat(url):
                return {'parse': 0, 'playUrl': '', 'url': url, 'header': headers}

            res = requests.get(url, headers=headers, timeout=120, verify=False)
            html = res.text
            current_url = res.url
            
            video_url = None
            
            json_matches = re.findall(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', html)
            for m in json_matches:
                if '.html' not in m: # 再次过滤
                    video_url = m
                    break
            
            if not video_url:
                param_matches = re.findall(r'(?:v|url|src)\s*=\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', html)
                for m in param_matches:
                    clean = m.replace('\\', '')
                    if not clean.startswith('http'):
                        clean = urljoin(current_url, clean)
                    if '.html' not in clean:
                        video_url = clean
                        break

            if video_url and self.isVideoFormat(video_url):
                return {
                    'parse': 0,
                    'playUrl': '',
                    'url': video_url,
                    'header': headers
                }
            
            return {
                'parse': 1, 
                'playUrl': '', 
                'url': url, 
                'header': headers
            }

        except Exception as e:
            print(f"Player error: {e}")
            return {'parse': 1, 'playUrl': '', 'url': url, 'header': headers}

    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        try:
            search_url = f"{self.host}/index.php/vod/type/id/2/wd/{requests.utils.quote(key)}/page/{pg}.html"
            res = requests.get(search_url, headers=self.headers, timeout=120)
            res.encoding = 'utf-8'
            vods = self._extractVideoItems(res.text)
            result['list'] = vods
            result['page'] = int(pg)
            result['pagecount'] = int(pg) + 1 if len(vods) > 0 else int(pg)
            result['limit'] = 20
            result['total'] = 9999
        except:
            pass
        return result

    def localProxy(self, params):
        return None