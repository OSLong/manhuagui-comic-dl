import requests
from bs4 import BeautifulSoup
from .chapter_type import CHAPTER_TYPE
import re
import lzstring
import STPyV8
import json
import os
import time
import random
import typing

class Comic():

    def _get_manhuagui_host(self):
        return 'https://www.manhuagui.com'
    
    def _get_request_header_user_agent(self):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'

    def __init__(self, opts):
        self.opts = opts
        self.comic_name = None
        pass

    session = requests.session()

    def _filtered_download_chapters(self, chapters):
        opts = self.opts

        # is_no_episode = opts.no_episode
        #  
        is_include_extra = opts.include_extra 
        is_include_episode = opts.include_episode
        is_include_volume = opts.include_volume
        is_include_undefined = opts.include_undefined

        included_types = []
        if is_include_episode:
            included_types += [CHAPTER_TYPE.EPISODE]
        if is_include_extra:
            included_types += [CHAPTER_TYPE.EXTRA]
        if is_include_volume:
            included_types += [CHAPTER_TYPE.VOLUME]
        if is_include_undefined:
            included_types += [CHAPTER_TYPE.UNDEFINED]

        chapters = [
            chapter 
            for chapter in chapters
            if chapter.chapter_type in included_types
        ]
        # print("Chapter after filter", chapters)
        return chapters

    def retrieve(self):
        opts = self.opts

        comic_id = opts.comic_id
        comic_detail_html = self._request_comic_detail_html(comic_id=comic_id)
        chapters = self._extract_chapters_from_html(comic_detail_html)

        chapters = self._filtered_download_chapters(chapters=chapters)

        for chapter in chapters:
            chapter.retrieve()

        print("Finished Comic Download : ",self.comic_name)


    def _request_comic_detail_html(self, comic_id: str):
        print("- Start Request Retrieve Comic Chapters : ", comic_id)
        host = self._get_manhuagui_host()
        comic_detail_url = f'%(host)s/comic/%(comic_id)s' %{
            'host': host,
            'comic_id': comic_id
        }
        headers = {
            'user-agent': self._get_request_header_user_agent()
        }
        session = self.session
        response = session.get(
            url=comic_detail_url,
            headers=headers
        )
        print("  Finish Request Retrieve Comic Chapters : ", comic_id)

        return response.content.decode('utf8', errors='ignore')
    
    def _extract_chapters_from_html(self, html_raw):
        soup = BeautifulSoup(html_raw, 'html.parser')

        book_title_element = soup.find('div', {'class': 'book-title'}).find('h1')
        self.comic_name = book_title_element.get_text()
        
        chapter_wrapper = soup.find('div', {'class': 'chapter'})

        result = []

        chapter_type = CHAPTER_TYPE.UNDEFINED
        for element in chapter_wrapper:

            is_chapter_type = element.name == 'h4'
            if is_chapter_type:
                chapter_type = element.get_text()
                continue

            element_class = element.get('class') or []

            is_chapter_container = 'chapter-list' in element_class
            if is_chapter_container:
                chapters = element.select('li > a')
                
                for chapter_element in chapters:
                    full_link = '%(host)s%(href)s' % {
                        'host': self._get_manhuagui_host(),
                        'href': chapter_element['href']
                    }
              
                    enum_chapter_type = CHAPTER_TYPE._get_chapter_type_from_chinese(chapter_type)
                    name = chapter_element['title']
                    count = chapter_element.find('i').get_text()[:-1]
                    chapter = Chapter(
                        comic=self,
                        name=name,
                        page_count=count,
                        chapter_type=enum_chapter_type,
                        chapter_type_raw=chapter_type,
                        url=full_link
                    )
                    result += [ chapter ]
        return result
  

# Save in same file , so i can use python typing 
# if save different file , will have recursive import error
# 
class Chapter():
    def __init__(self, comic: Comic, name, chapter_type, url, chapter_type_raw=None, page_count=None ):
        self.comic = comic
        self.name = name
        self.chapter_type = chapter_type
        self.chapter_type_raw = chapter_type_raw
        self.url = url
        self.page_count = page_count


    def __str__(self):
        return json.dumps({
            'name': self.name,
            'chapter_type_raw': self.chapter_type_raw,
            'chapter_type': self.chapter_type.value,
            'url': self.url,
            'page_count': self.page_count
        })
    
    def __repr__(self):
        return str(self)
    
    def _request_chapter_page_html(self):
        print("  - Start Request comic chapter detail : ", self.comic.comic_name, ' -- ',self.name)
        headers = {
            'user-agent': self.comic._get_request_header_user_agent()
        }
        session = self.comic.session
        response = session.get(
            url=self.url,
            headers=headers
        )
        print("    Finish Request comic chapter detail : ", self.comic.comic_name, ' -- ',self.name)

        return response.content.decode('utf8', errors='ignore')

    def _extract_info_from_html(self, raw_html):
        """
        This function , i follow here : 
            https://github.com/kimklai/manhuagui/blob/master/src/mhg.py#L127
        """
        raw_content = raw_html
        res = re.search(
            r'<script type="text\/javascript">window\["\\x65\\x76\\x61\\x6c"\](.*\)) <\/script>', raw_content).group(1)

        lz_encoded = re.search(
            r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", res).group(1)
        lz_decoded = lzstring.LZString().decompressFromBase64(lz_encoded)
        res = re.sub(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)",
                     "'%s'.split('|')" % (lz_decoded), res)
        
        # code = node.get_node_output(res)
        with STPyV8.JSContext() as ctx:
            code = ctx.eval(res)
        
        pages_opts = json.loads(
            re.search(r'^SMH.imgData\((.*)\)\.preInit\(\);$', code).group(1))
        return pages_opts
    
    def _get_cache_dir(self):
        return './caches'
    
    def _get_chapter_cache_file_name(self):
        comic_name = self.comic.comic_name
        chapter_name = self.name

        cache_dir = self._get_cache_dir()
        current_comic_cache_dir = f'{cache_dir}/{comic_name}'
        chapter_cache_file_name = f'{current_comic_cache_dir}/{chapter_name}.json'
        return chapter_cache_file_name

    def _cache_chapter_detail_info(self, chapter_info: dict):
        chapter_cache_file_name = self._get_chapter_cache_file_name()

        comic_cache_dir = os.path.dirname(chapter_cache_file_name)
        if not os.path.exists(comic_cache_dir):
            os.makedirs(comic_cache_dir, exist_ok=True)

        with open(chapter_cache_file_name, 'w') as cache_file:
            cache_file.write(json.dumps(chapter_info, indent=2))
    
    def _read_get_chapter_cache(self):
        # return False
        chapter_cache_file_name = self._get_chapter_cache_file_name()
        if not os.path.exists(chapter_cache_file_name):
            return False
        result = None
        with open(chapter_cache_file_name, 'r') as cache_file:
            result = json.loads(cache_file.read())
        
        return result
    
    def _get_mhg_image_server(self):
        return 'https://eu1.hamreus.com'

    def _get_data_dir(self):
        return './data'
    

    def _build_image_download_url(self, chapter_info, image_name):
        host = self._get_mhg_image_server()
        path = chapter_info.get('path')
        download_url = ''.join([
            host,
            path,
            image_name
        ])
        return download_url
    
    def _build_image_file_name(self, chapter_info, image_name):
        data_dir = self._get_data_dir()
        comic_name = self.comic.comic_name
        chapter_name = self.name
        
        image_file_path = '/'.join([
            data_dir,
            comic_name,
            'images',
            self.chapter_type.value,
            chapter_name,
            image_name
        ])
        return image_file_path
    
    def _get_image_download_delay_time(self):
        random_delay_times = [500, 1000]
        return random.randrange(*random_delay_times) / 1000
    

    def _request_download_image(self, chapter_info, download_url):
        """
        This function i follow from : 
                https://github.com/kimklai/manhuagui/blob/master/src/mhg.py#L254
        """
        # import http.client

        # def patch_send():
        #     old_send= http.client.HTTPConnection.send
        #     def new_send( self, data ):
        #         print(data.decode())
        #         return old_send(self, data) #return is not necessary, but never hurts, in case the library is changed
        #     http.client.HTTPConnection.send= new_send

        # patch_send()

        print('    - Start download image : ', self.name , f' Total: ( {chapter_info['len']} )', ' -- ', download_url)
        params={
            # 'cid': chapter_info['cid'],
            # 'md5': chapter_info['sl']['m'],
            'm': chapter_info['sl']['m'],
            'e': chapter_info['sl']['e'],
        },
        headers={
            'Referer': self.comic._get_manhuagui_host(),
            'user-agent':self.comic._get_request_header_user_agent()
        }
        session = self.comic.session
        response = session.get(
            url=download_url, 
            headers=headers,
            params=params
        )
        # if response.status_code != 200:
        #     self._sleep()
        #     return self._request_download_image(
        #         download_url=download_url,
        #         chapter_info=chapter_info
        #     )
    
        
        print('      Finish download image : ', self.name, ' -- ', download_url)
        return response.content

    def _sleep(self):
        delay = self._get_image_download_delay_time()
        print("        - Delay : ", delay)
        time.sleep(delay)

    def retrieve(self):
        chapter_info = self._read_get_chapter_cache()
        if not chapter_info:
            raw_html = self._request_chapter_page_html()
            chapter_info = self._extract_info_from_html(raw_html=raw_html)
            self._cache_chapter_detail_info(chapter_info)

        for image_name in chapter_info.get('files'):
            image_file_path = self._build_image_file_name(
                chapter_info=chapter_info,
                image_name=image_name
            )
            if os.path.exists(image_file_path):
                continue

            image_file_dir = os.path.dirname(image_file_path)
            if not os.path.exists(image_file_dir):
                os.makedirs(image_file_dir)
            
            image_download_url = self._build_image_download_url(
                chapter_info=chapter_info,
                image_name=image_name
            )

            image_data = self._request_download_image(
                chapter_info=chapter_info,
                download_url=image_download_url
            )

            with open(image_file_path, 'wb') as image_file:
                image_file.write(image_data)

            # print(f'Downloaded : {self.comic.comic_name} - {self.name} - {image_name}', image_download_url)

            self._sleep()
            pass

        pass