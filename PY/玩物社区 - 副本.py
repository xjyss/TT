import json
import re
import sys
import hashlib
from base64 import b64decode, b64encode
from urllib.parse import urlparse
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider as BaseSpider

img_cache = {}

class Spider(BaseSpider):
    def init(self, extend=""):
        try:
            self.proxies = json.loads(extend)
        except:
            self.proxies = {}
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})

    def getName(self):
        return "玩物社区"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def get_working_host(self):
        dynamic_urls = [
            'https://thu.ukjgajhd.cc',
            'https://wanwusm.org',
            'https://wanwusm.net',
            'https://wanwusq.net',
            'https://smwanwu.net',
            'https://wanwusm.io',
            'https://wanwuu.com',
            'https://wanwu47.com'
        ]
        for url in dynamic_urls:
            try:
                response = self.session.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                if response.status_code == 200:
                    return url
            except Exception:
                continue
        return dynamic_urls[0]

    def homeContent(self, filter):
        try:
            self.session.get(self.host, proxies=self.proxies, timeout=6)
        except:
            pass
        classes = [
            {'type_name': 'AI短剧', 'type_id': '/ai/all/'},
            {'type_name': '调教av','type_id': '/videos/tiaojiao-av/'},
            {'type_name': 'AI成人短剧','type_id': '/ai/ai-duanju/'},
            {'type_name': 'AI漫剧','type_id': '/ai/ai-manju/'},
            {'type_name': 'AI换脸','type_id': '/ai/ai-huanlian/'},
            {'type_name': 'AI美女','type_id': '/ai/ai-meinv/'},
            {'type_name': '直播回放','type_id': '/videos/zhibo-huifang/'},
            {'type_name': '国产sm','type_id': '/videos/guochan-sm/'},
            {'type_name': '日韩sm','type_id': '/videos/rihan-sm/'},
            {'type_name': 'SM','type_id': '/videos/search/sm/'},
            {'type_name': '人妻','type_id': '/videos/search/人妻/'},
            {'type_name': '凌辱','type_id': '/videos/search/凌辱/'},
            {'type_name': '欧美sm','type_id': '/videos/oumei-sm/'},
            {'type_name': '动漫sm','type_id': '/videos/dongman-sm/'},
            {'type_name': '日韩AV','type_id': '/porn/rihan-av/'},
            {'type_name': '欧美无码','type_id': '/porn/oumei-wuma/'},
            {'type_name': '国产探花','type_id': '/porn/guochan-tanhua/'},
            {'type_name': '黑人专区','type_id': '/porn/heiren-zhuanqu/'},
            {'type_name': '绿帽淫妻','type_id': '/porn/lvmao-yinqi/'},
            {'type_name': '黑料吃瓜','type_id': '/porn/chigua-baoliao/'},
            {'type_name': '玩物畅聊','type_id': '/posts/wanwu-changliao/'},
            {'type_name': '恋足原创','type_id': '/posts/lianzu-yuanchuang/'},
            {'type_name': '抖M天堂','type_id': '/posts/doum-tiantang/'},
            {'type_name': '女王天地','type_id': '/posts/nvwang-tiandi/'}
        ]
        return {'class': classes, 'list': []}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            if '@folder' in tid:
                v = self.getfod(tid.replace('@folder', ''))
                return {'list': v, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(v)}

            pg = int(pg) if pg else 1

            if tid.startswith('http'):
                base_url = tid.rstrip('/')
            else:
                path = tid if tid.startswith('/') else f"/{tid}"
                base_url = f"{self.host}{path}".rstrip('/')

            if pg == 1:
                url = f"{base_url}/"
            else:
                url = f"{base_url}/page/{pg}/"

            # 超时改为6秒
            response = self.session.get(url, headers=self.headers, proxies=self.proxies, timeout=6)
            if response.status_code != 200:
                return {'list': [], 'page': pg, 'pagecount': 30, 'limit': 90, 'total': 0}

            data = self.getpq(response.text)
            videos = self.getlist(data('li'), tid)

            return {'list': videos, 'page': pg, 'pagecount': 30, 'limit': 90, 'total': 1000}
        except Exception as e:
            return {'list': [], 'page': pg, 'pagecount': 999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            raw_id = ids[0]
            # 分割：播放链接||固定播放标题=视频
            if '||' in raw_id:
                url_part, _ = raw_id.split('||',1)
            else:
                url_part = raw_id
            url = url_part if url_part.startswith('http') else f"{self.host}{url_part}"
            # 播放列表固定名字叫【视频】
            plist = [f"视频${url}"]
            play_url = '#'.join(plist)
            return {'list': [{'vod_play_from': '立即播放', 'vod_play_url': play_url, 'vod_content': ''}]}
        except:
            return {'list': [{'vod_play_from': '立即播放', 'vod_play_url': '获取失败'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            pg = int(pg) if pg else 1
            if pg == 1:
                url = f"{self.host}/videos/search/{key}/"
            else:
                url = f"{self.host}/videos/search/{key}/page/{pg}/"
            # 搜索超时缩短到8秒
            response = self.session.get(url, headers=self.headers, proxies=self.proxies, timeout=8)
            return {'list': self.getlist(self.getpq(response.text)('li'), tid=""), 'page': pg, 'pagecount': 9999}
        except:
            return {'list': [], 'page': pg, 'pagecount': 9999}

    def playerContent(self, flag, id, vipFlags):
        # 优化：优先判断视频直链，减少多余处理
        if self.isVideoFormat(id):
            return {'parse': 0, 'url': id, 'header': self.headers}
        parse = 0 if self.isVideoFormat(id) else 1
        url = self.proxy(id) if '.m3u8' in id else id
        return {'parse': parse, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        try:
            type_ = param.get('type')
            url = param.get('url')
            if type_ == 'cache':
                key = param.get('key')
                if content := img_cache.get(key):
                    return [200, 'image/jpeg', content]
                return [404, 'text/plain', b'Expired']
            elif type_ == 'img':
                real_url = self.d64(url) if not url.startswith('http') else url
                res = self.session.get(real_url, headers=self.headers, proxies=self.proxies, timeout=10)
                content = self.aesimg(res.content)
                return [200, 'image/jpeg', content]
            elif type_ == 'm3u8':
                return self.m3Proxy(url)
            else:
                return self.tsProxy(url)
        except:
            return [404, 'text/plain', b'']

    def proxy(self, data, type='m3u8'):
        if data and self.proxies:
            return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        return data

    def m3Proxy(self, url):
        url = self.d64(url)
        res = self.session.get(url, headers=self.headers, proxies=self.proxies, timeout=8)
        data = res.text
        base = res.url.rsplit('/', 1)[0]
        lines = []
        # splitlines优化，跳过空行
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                lines.append(line)
                continue
            if not line.startswith('http'):
                line = f"{base}/{line}"
            lines.append(self.proxy(line, 'ts'))
        return [200, "application/vnd.apple.mpegurl", '\n'.join(lines)]

    def tsProxy(self, url):
        return [200, 'video/mp2t', self.session.get(self.d64(url), headers=self.headers, proxies=self.proxies).content]

    def e64(self, text):
        return b64encode(str(text).encode()).decode()

    def d64(self, text):
        return b64decode(str(text).encode()).decode()

    def aesimg(self, data):
        if len(data) < 16:
            return data
        keys = [(b'f5d965df75336270', b'97b60394abc2fbe1'), (b'75336270f5d965df', b'abc2fbe197b60394')]
        for k, v in keys:
            try:
                dec = unpad(AES.new(k, AES.MODE_CBC, v).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8') or dec.startswith(b'\x89PNG'):
                    return dec
            except:
                pass
            try:
                dec = unpad(AES.new(k, AES.MODE_ECB).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8'):
                    return dec
            except:
                pass
        return data

    def getlist(self, data, tid=''):
        videos = []
        is_folder = '/mrdg' in (tid or '')
        for k in data.items():
            card_html = k.outer_html() if hasattr(k, 'outer_html') else str(k)
            a = k if k.is_('a') else k('a').eq(0)
            href = a.attr('href')
            # 列表标题：网页原生标题，不固定
            title = k('h2').text() or k('.post-card-title').text() or k('.post-title').text()
            if not title and k.is_('a'):
                title = k.text()
            if href and title:
                img = self.getimg(k('script').text(), k, card_html)
                # vod_id 存：播放链接||固定播放标题，detail读取后写死剧集名为视频
                videos.append({
                    'vod_id': f"{href}||视频",
                    'vod_name': title.strip(),
                    'vod_pic': img,
                    'vod_remarks': (k('.post-card-info>span').eq(1).text() or '').strip('•'),
                    'vod_tag': 'folder' if is_folder else '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def getfod(self, id):
        url = f"{self.host}{id}"
        resp = self.session.get(url, headers=self.headers, proxies=self.proxies)
        data = self.getpq(resp.text)
        videos = []
        for i, h2 in enumerate(data('.post-content h2').items()):
            p_txt = data('.post-content p').eq(i * 2)
            p_img = data('.post-content p').eq(i * 2 + 1)
            p_html = p_img.outer_html() if hasattr(p_img, 'outer_html') else str(p_img)
            link = p_txt('a').attr('href')
            title = p_txt.text().strip()
            videos.append({
                'vod_id': f"{link}||视频",
                'vod_name': title,
                'vod_pic': self.getimg('', p_img, p_html),
                'vod_remarks': h2.text().strip()
            })
        return videos

    def getimg(self, text, elem=None, html_content=None):
        if m := re.search(r"loadBannerDirect\('([^']+)'", text or ''):
            return self._proc_url(m.group(1))
        if html_content is None and elem is not None:
            html_content = elem.outer_html() if hasattr(elem, 'outer_html') else str(elem)
        if not html_content:
            return ''
        html_content = html_content.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')
        if 'data:image' in html_content:
            m = re.search(r'(data:image/[a-zA-Z0-9+/=;,]+)', html_content)
            if m:
                return self._proc_url(m.group(1))
        m = re.search(r'(https?://[^"\'\s)]+\.(?:jpg|png|jpeg|webp))', html_content, re.I)
        if m:
            return self._proc_url(m.group(1))
        if 'url(' in html_content:
            m = re.search(r'url\s*\(\s*[\'"]?([^"\'\)]+)[\'"]?\s*\)', html_content, re.I)
            if m:
                return self._proc_url(m.group(1))
        return ''

    def _proc_url(self, url):
        if not url:
            return ''
        url = url.strip('\'" ')
        if url.startswith('data:'):
            try:
                _, b64_str = url.split(',', 1)
                raw = b64decode(b64_str)
                if not (raw.startswith(b'\xff\xd8') or raw.startswith(b'\x89PNG') or raw.startswith(b'GIF8')):
                    raw = self.aesimg(raw)
                key = hashlib.md5(raw).hexdigest()
                img_cache[key] = f"{self.getProxyUrl()}&type=cache&key={key}"
            except:
                return ""
        if not url.startswith('http'):
            url = f"{self.host}{url}" if url.startswith('/') else f"{self.host}/{url}"
        return f"{self.getProxyUrl()}&url={self.e64(url)}&type=img"

    def getpq(self, data):
        try:
            return pq(data)
        except:
            return pq(data.encode('utf-8'))
