import sys
import re
import urllib.parse
from base.spider import Spider
#http://www.qiyoudy.info
class Spider(Spider):
    def __init__(self):
        self.name = '奇优影院'
        self.host = 'http://www.qiyou03.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        classes = [
            {'type_id': '1', 'type_name': '电影'},
            {'type_id': '2', 'type_name': '电视剧'},
            {'type_id': '3', 'type_name': '动漫'},
            {'type_id': '4', 'type_name': '综艺'},
            {'type_id': '6', 'type_name': '伦理'}
        ]
        return {'class': classes}

    def homeVideoContent(self):
        res = self.fetch(self.host)
        html = res.text
        videos = []
        pattern = r'<a class="stui-vodlist__thumb[^>]*data-original="([^"]+)"[^>]*href="/view/(\d+)\.html"[^>]*title="([^"]+)">.*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, html, re.DOTALL)
        for pic, vod_id, name, remarks in matches:
            videos.append({
                'vod_id': vod_id,
                'vod_name': name,
                'vod_pic': pic,
                'vod_remarks': remarks.strip()
            })
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        if str(pg) == '1':
            url = f"{self.host}/list/{tid}.html"
        else:
            url = f"{self.host}/list/{tid}_{pg}.html"

        res = self.fetch(url)
        html = res.text

        videos = []
        pattern = r'<a class="stui-vodlist__thumb[^>]*data-original="([^"]+)"[^>]*href="/view/(\d+)\.html"[^>]*title="([^"]+)">.*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, html, re.DOTALL)
        for pic, vod_id, name, remarks in matches:
            videos.append({
                'vod_id': vod_id,
                'vod_name': name,
                'vod_pic': pic,
                'vod_remarks': remarks.strip()
            })
        return {'list': videos}

    def detailContent(self, ids):
        vid = ids[0]
        url = f"{self.host}/view/{vid}.html"
        res = self.fetch(url)
        html = res.text

        vod = {
            'vod_id': vid,
            'vod_name': '',
            'vod_pic': '',
            'vod_content': '',
            'type_name': '',
            'vod_area': '',
            'vod_year': '',
            'vod_actor': '',
            'vod_director': '',
            'vod_play_from': '',
            'vod_play_url': ''
        }

        name_match = re.search(r'<meta content="([^"]+)" property="og:title">', html)
        if name_match: 
            vod['vod_name'] = name_match.group(1)

        pic_match = re.search(r'<meta content="([^"]+)" property="og:image">', html)
        if pic_match:
            vod['vod_pic'] = pic_match.group(1)

        desc_match = re.search(r'<meta content="([^"]+)" property="og:description">', html)
        if desc_match:
            vod['vod_content'] = desc_match.group(1).replace(vod['vod_name'] + '讲述了', '').strip()

        type_match = re.search(r'类型：</span>\s*<a[^>]+>([^<]+)</a>', html)
        if type_match:
            vod['type_name'] = type_match.group(1)

        area_match = re.search(r'地区：</span>([^<]+)<', html)
        if area_match:
            vod['vod_area'] = area_match.group(1).strip()

        year_match = re.search(r'年份：</span>([^<]+)<', html)
        if year_match:
            vod['vod_year'] = year_match.group(1).strip()

        actor_match = re.search(r'主演：</span>([^<]+)<', html)
        if actor_match:
            vod['vod_actor'] = actor_match.group(1).strip()

        director_match = re.search(r'导演：</span>([^<]+)<', html)
        if director_match:
            vod['vod_director'] = director_match.group(1).strip()

        tabs_pattern = r'<a data-toggle="tab" href="#(down\d+)">([^<]+)</a>'
        tabs = re.findall(tabs_pattern, html)

        play_froms = []
        play_urls = []

        for tab_id, tab_name in tabs:
            play_froms.append(tab_name)
            list_pattern = f'id="{tab_id}"[^>]*>(.*?)</div>'
            list_match = re.search(list_pattern, html, re.DOTALL)
            ep_list = []
            if list_match:
                list_html = list_match.group(1)
                ep_pattern = r'<a href="/play/([^"]+)\.html"[^>]*title="([^"]+)"'
                eps = re.findall(ep_pattern, list_html)
                for ep_url, ep_title in eps:
                    ep_list.append(f"{ep_title}${ep_url}")
            play_urls.append('#'.join(ep_list))

        vod['vod_play_from'] = '$$$'.join(play_froms)
        vod['vod_play_url'] = '$$$'.join(play_urls)

        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/search.php"
        data = {"searchword": key}
        res = self.fetch(url, data=data, method="POST")  
        html = res.text

        videos = []
        pattern = r'<a class="stui-vodlist__thumb[^>]*data-original="([^"]+)"[^>]*href="/view/(\d+)\.html"[^>]*title="([^"]+)">.*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, html, re.DOTALL)
        for pic, vod_id, name, remarks in matches:
            videos.append({
                'vod_id': vod_id,
                'vod_name': name,
                'vod_pic': pic,
                'vod_remarks': remarks.strip()
            })
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        url = f"{self.host}/play/{id}.html"
        res = self.fetch(url)
        html = res.text

        iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', html, re.IGNORECASE)
        if iframe_match:
            play_url = iframe_match.group(1)
            return {'parse': 1, 'url': play_url, 'header': self.headers}

        return {'parse': 1, 'url': url, 'header': self.headers}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None