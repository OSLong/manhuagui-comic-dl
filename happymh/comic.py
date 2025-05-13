import urllib.parse
import ebooklib.epub
import requests
import re
import lzstring
import STPyV8
import json
import os
import time
import random
import typing
import ebooklib
import urllib
import bs4
from collections import namedtuple
from . import chapter_type
# import cloudscraper

Components = namedtuple(
    typename='Components', 
    field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
)


class Comic():

    def _get_happymh_host(self):
        return 'https://m.happymh.com'
    
    def _get_request_header_user_agent(self):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'
        # return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'

    def _load_happy_mh_cookies(self):
        cookie_file_path = './happy_mh_cookie.txt'
        file = open(cookie_file_path, 'r+')
        cookie_raw_text = file.read()
        if not cookie_raw_text:
            raise ValueError("Please set up cookie raw text for use Happy MH .")
        
        cookies = {}
        for cookie in cookie_raw_text.split(';'):
            key, val = cookie.split('=')
            cookies[key] = val
        return cookies

    def __init__(self, opts):
        self.opts = opts
        self.comic_name = None
        self.comic_id = opts.comic_id
        pass

    def _delay(self):
        random_delay_times = [500, 1000]
        to_delay = random.randrange(*random_delay_times) / 1000
        print(f"- Delay : {to_delay}")
        time.sleep(to_delay)

    session = requests.session()

    def _filtered_download_chapters(self, chapters):
        opts = self.opts


        if opts.start_from:
            chapters = [
                chapter
                for chapter in chapters
                if chapter.order >= int(opts.start_from)
            ]

        if opts.stop_at:
            chapters = [
                chapter
                for chapter in chapters
                if chapter.order <= int(opts.stop_at)
            ]
        # print("Chapter after filter", chapters)
        return chapters
    
    def _adapt_to_chapter_class(self, comic_info, chapter_info): 
        return  Chapter(
            comic=self,
            name=chapter_info.get('chapterName'),
            code=chapter_info.get('codes'),
            order=chapter_info.get('order')
        )

    def process(self):
        opts = self.opts

        comic_id = opts.comic_id

        comic_info_html_raw = self.request_comic_detail_html(comic_id)
        comic_info = self._extract_comic_info_from_html(comic_info_html_raw)
        print("Comic INfo : ", comic_info)

        chapter_infos = self.request_comic_chapters(comic_id=comic_id, comic_info=comic_info)
        
        chapters = []
        for chapter_info in chapter_infos:
            chapter = self._adapt_to_chapter_class(comic_info=comic_info, chapter_info=chapter_info)
            chapters += [chapter]
        chapters = self._filtered_download_chapters(chapters=chapters)


        print("Chapter Now is : ", chapters)

        # For Testing
        # chapters = chapters[1:2]

        for chapter in chapters:
            chapter.process()
            # chapter._sleep()

        # print("Finished Comic Download : ",self.comic_name)
        
        if opts.export_to_epub:
            for chapter in chapters:
                chapter.export_to_epub()
            print("Finish Export EPUB FILE : ",self.comic_name)

    def _get_sample_comic_detail_html(self):
        json_text = open('./sample/happymh_sample.json', 'rb').read().decode('utf8', errors='ignore')
        return json.loads(json_text)
    
    
    def _get_cache_dir(self):
        return './caches'
    
    def _extract_comic_info_from_html(self, html_raw):
        soup = bs4.BeautifulSoup(html_raw, 'html.parser')
        title = soup.find('h2', {'class': 'mg-title'})
        comic_id = soup.find('input', {'name': 'code'}).get('value')
        self.comic_name = title.text
        return {
            'comic_id': comic_id,
            'comic_title': title.text
        }
    
    def _get_comic_cache_dir(self, comic_id):
        CACHE_DIR = self._get_cache_dir()

        comic_cache_dir = f'{CACHE_DIR}/{comic_id}'
        return comic_cache_dir

    def _get_comic_detail_html_from_cache_name(self, comic_id):
        comic_cache_dir = self._get_comic_cache_dir(comic_id)
        if not os.path.exists(comic_cache_dir):
            os.makedirs(comic_cache_dir, exist_ok=True)
        cache_name = f'{comic_cache_dir}/detail.html'
        return cache_name

    def request_comic_detail_html(self, comic_id):
        cache_file_name = self._get_comic_detail_html_from_cache_name(comic_id=comic_id)
        if os.path.exists(cache_file_name):
            return open(cache_file_name, 'rb').read().decode(errors='ignore')
    
        host = self._get_happymh_host()
        comic_detail_url = f'%(host)s/manga/%(comic_id)s' %{
                'host': host,
                'comic_id': comic_id,
        }
        headers = {
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',

            'user-agent': self._get_request_header_user_agent(),
            # 'referer': host
        }
        cookies = self._load_happy_mh_cookies()
        response = requests.get(
            comic_detail_url,
            headers=headers,
            cookies=cookies
        )
        open(cache_file_name, 'wb').write(response.content)
        html_raw = response.content.decode(errors='ignore')
        return html_raw
    
    def request_comic_chapters(self, comic_id: str, comic_info):
        opts = self.opts
        if opts.use_sample:
            return self._get_sample_comic_detail_html()
        
        session = self.session
 
        print("- Start Request Retrieve Comic Chapters : ", comic_id)
        host = self._get_happymh_host()
        next_page = 1
        all_chapters = []
        while next_page:
            query_params = {
                'code': comic_id, 
                'page': next_page,
                'lang': 'cn',
                'order': 'desc'
            }
            comic_chapter_url = f'%(host)s/v2.0/apis/manga/chapterByPage' %{
                'host': host,
            }
            headers = {
                'user-agent': self._get_request_header_user_agent(),
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'dnt': '1',
                'priority': 'u=1, i',
                'referer': 'https://m.happymh.com/',
                'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-arch': 'x86',
                'sec-ch-ua-bitness': '64',
                'sec-ch-ua-full-version': '136.0.3240.64',
                'sec-ch-ua-full-version-list': 'Chromium;v="136.0.7103.93", "Microsoft Edge";v="136.0.3240.64", "Not.A/Brand";v="99.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '',
                'sec-ch-ua-platform': 'Windows',
                'sec-ch-ua-platform-version': '15.0.0',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-id': '1747150475680',
                'x-requested-with': 'XMLHttpRequest'
            }
            cookies = self._load_happy_mh_cookies()
            response = requests.get(
                comic_chapter_url,
                params=query_params,
                headers=headers,
                cookies=cookies
            )

            print("Response JSon is ", response.content)
            response_json = json.loads(response.content)

            data = response_json.get('data')
            chapters = data.get('items')
            is_end = data.get('isEnd')

            all_chapters += chapters
            # break
            
            # session.cookies
            next_page += 1
            if is_end:
                next_page = None 
            self._delay()

        return all_chapters
    
  

# Save in same file , so i can use python typing 
# if save different file , will have recursive import error
# 
class Chapter():
    def __init__(self, comic: Comic, name, code, order, page_count=None ):
        self.comic = comic
        self.name = name
        self.chapter_type = chapter_type.CHAPTER_TYPE.EPISODE
        # self.chapter_type_raw = chapter_type_raw
        self.code = code
        self.order = order
        self.page_count = page_count

    
    def __str__(self):
        return json.dumps({
            'name': self.name,
            'code': self.code,
        })
    
    def __repr__(self):
        return str(self)
     
    
    def _request_chapter_page_data(self):
        print("  - Start Request comic chapter detail : ", self.comic.comic_id, ' -- ',self.name)
        headers = {
            'user-agent': self.comic._get_request_header_user_agent(),
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://m.happymh.com/',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-arch': 'x86',
            'sec-ch-ua-bitness': '64',
            'sec-ch-ua-full-version': '136.0.3240.64',
            'sec-ch-ua-full-version-list': 'Chromium;v="136.0.7103.93", "Microsoft Edge";v="136.0.3240.64", "Not.A/Brand";v="99.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '',
            'sec-ch-ua-platform': 'Windows',
            'sec-ch-ua-platform-version': '15.0.0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-id': '1747150475680',
            'x-requested-with': 'XMLHttpRequest'
        }
        params = {
            'code': self.code,
            'v': 'v3.1818134'
        }
        host = self.comic._get_happymh_host()
        session = self.comic.session

        # manga_read_url = f'{host}/mangaread/{self.code}'
        # manga_read_response = session.get(
        #     url=manga_read_url,
        #     headers=headers,
        #     params=params,
        #     cookies=self.comic._load_happy_mh_cookies()
        # )

        url = f'{host}/v2.0/apis/manga/reading'
        response = session.get(
            url=url,
            headers=headers,
            params=params,
            cookies=self.comic._load_happy_mh_cookies()
        )
        print("    Finish Request comic chapter detail : ", self.comic.comic_name, ' -- ',self.name)

        json_response = json.loads(response.content.decode('utf8', errors='ignore'))
        
        success = json_response.get('status') == 0

        if not success:
            raise ValueError("==== Failed on ", self.name)
        return json_response
    
    def _get_cache_dir(self):
        return './caches'
    
    def _get_chapter_cache_file_name(self):
        comic_name = self.comic.comic_id
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
        return self.comic._get_happymh_host()

    def _get_data_dir(self):
        return './data'

    
    def _get_data_image_dir(self):
        data_dir = self._get_data_dir()
        comic_name = self.comic.comic_name
        return '/'.join([
            data_dir,
            comic_name,
            'images',
        ])

    def _build_image_file_name(self, chapter_info, index, image_url):
        chapter_name = self.name
        
        index_name = str(index).rjust(4, '0')
        image_name = os.path.basename(image_url).split('?')[0]
        name = '-'.join([index_name, image_name])
        image_file_path = '/'.join([
            self._get_data_image_dir(),
            self.chapter_type.value,
            chapter_name,
            name
        ])
        return image_file_path
    
    def _get_image_download_delay_time(self):
        random_delay_times = [500, 1000]
        return random.randrange(*random_delay_times) / 1000
    

    def _request_download_image(self, chapter_info, download_url):
        print('    - Start download image : ', self.name , f' Total: ( {self.page_count} )', ' -- ', download_url)
        params={
            # 'cid': chapter_info['cid'],
            # 'md5': chapter_info['sl']['m'],
            # 'm': chapter_info['sl']['m'],
            # 'e': chapter_info['sl']['e'],
        },
        headers={
            'user-agent':self.comic._get_request_header_user_agent(),
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://m.happymh.com/',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-arch': 'x86',
            'sec-ch-ua-bitness': '64',
            'sec-ch-ua-full-version': '136.0.3240.64',
            'sec-ch-ua-full-version-list': 'Chromium;v="136.0.7103.93", "Microsoft Edge";v="136.0.3240.64", "Not.A/Brand";v="99.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '',
            'sec-ch-ua-platform': 'Windows',
            'sec-ch-ua-platform-version': '15.0.0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-id': '1747150475680',
            'x-requested-with': 'XMLHttpRequest'
        }
        session = self.comic.session
        response = session.get(
            url=download_url, 
            headers=headers,
            cookies=self.comic._load_happy_mh_cookies()
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

    def process(self):
        chapter_info = self._read_get_chapter_cache()
        # chapter_info = False
        if not chapter_info:
            chapter_info = self._request_chapter_page_data()
            self._cache_chapter_detail_info(chapter_info)
            # After request from internet , delay it
            self._sleep()

        data = chapter_info.get('data')
        image_infos = data.get('scans')

        self.page_count = len(image_infos)

        for index , image_info in enumerate(image_infos):
            image_url = image_info['url']
            image_file_path = self._build_image_file_name(
                chapter_info=chapter_info,
                index=index+1,
                image_url=image_url,
            )
            if os.path.exists(image_file_path):
                continue

            image_file_dir = os.path.dirname(image_file_path)
            if not os.path.exists(image_file_dir):
                os.makedirs(image_file_dir)
            
            # image_download_url = self._build_image_download_url(
            #     chapter_info=chapter_info,
            #     image_url=image_url
            # )
            image_download_url = image_url

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

    def _get_chapter_downloaded_data_images_file_names(self):
        comic_image_dir = self._get_data_image_dir()
        chapter_image_dir = '/'.join([
            comic_image_dir, 
            self.chapter_type.value,
            self.name
        ])

        is_valid_dir =  os.path.exists(chapter_image_dir) and os.path.isdir(chapter_image_dir)
        if not is_valid_dir:
            raise IOError(f'Directory Invalid : {chapter_image_dir}',)
        
        # Change to full path
        image_file_names = [
            os.path.join(chapter_image_dir, image_file_name)
            for image_file_name in os.listdir(chapter_image_dir)
        ]

        # filter is file only
        image_file_names = [
            image_file_name
            for image_file_name in image_file_names
            if os.path.isfile(image_file_name)
        ]

        # sort by date
        image_file_names.sort(
            key=lambda image_file_name:
            os.path.getmtime(image_file_name)
        )
        return image_file_names

    def _build_epub_book(self, chapter_info):
        image_file_paths = self._get_chapter_downloaded_data_images_file_names()

        epub = ebooklib.epub
        ebook = epub.EpubBook()

        comic = self.comic

        title = ' - '.join([
            comic.comic_name,
            self.name
        ])
        ebook.set_title(title=title)
        ebook.set_identifier('-'.join([str(self.name),str(self.comic.comic_id)]))
        ebook.set_language('cn')

        # ebook.add_author(comic.comic_author)

        if image_file_paths:
            cover_image_path = image_file_paths[0]
            image_content = open(cover_image_path, 'rb').read()
            ebook.set_cover('static/cover', image_content, False)

        to_added_pages, to_added_images = [], []

        split_page_by_image = self.comic.opts.split_page_by_image

        def _use_options_split_page_by_image(image_file_paths):
            _to_added_pages = []
            _to_added_images = []
            for index, image_file_path in enumerate(image_file_paths):
                page_number = str(index + 1).rjust(4, '0')
                image_file_name = os.path.basename(image_file_path)

                # In case that in image url use encode uri component like : %20 = ' '
                # i decode it to normal name first 
                # 
                image_file_name = urllib.parse.unquote(image_file_name)

                epub_internal_image_path = f'static/{image_file_name}'
            
                
                page_uid = f'{self.name} - {page_number}'
                page = epub.EpubHtml(title=page_number, uid=page_uid, file_name=f"{page_number}.xhtml", content='' )
                page.content += (
                    f'<figure>'
                        f'<img src="{epub_internal_image_path}" width="100%" height="auto" style="object-fit: contain">'
                        f'<figcaption{page_number} / {chapter_info["len"]}</figcaption>'
                    " </figure>"
                )
                

                image_content = open(image_file_path, 'rb').read()
                image = epub.EpubImage(
                    uid=image_file_name,
                    file_name=epub_internal_image_path,
                    content=image_content
                )
                _to_added_images += [image]
                _to_added_pages += [page]

            return _to_added_pages, _to_added_images

        def _use_options_no_split_page(image_file_paths):
            _to_added_images = []

            page_uid = f'{self.name} - content'
            page = epub.EpubHtml(title='Content', uid=page_uid, file_name=f"Content.xhtml", content='' )
            

            for index, image_file_path in enumerate(image_file_paths):
                page_number = str(index + 1).rjust(4, '0')
                image_file_name = os.path.basename(image_file_path)

                # In case that in image url use encode uri component like : %20 = ' '
                # i decode it to normal name first 
                # 
                image_file_name = urllib.parse.unquote(image_file_name)

                epub_internal_image_path = f'static/{image_file_name}'
            
                # if not page or split_by_image:
                page.content += (
                    f'<figure>'
                        f'<img src="{epub_internal_image_path}" width="100%" height="auto" style="object-fit: contain">'
                        f'<figcaption>{page_number} / {self.page_count}</figcaption>'
                    " </figure>"
                )

                image_content = open(image_file_path, 'rb').read()
                image = epub.EpubImage(
                    uid=image_file_name,
                    file_name=epub_internal_image_path,
                    content=image_content
                )

                _to_added_images += [image]

            return [page], _to_added_images

        
        if split_page_by_image:
            to_added_pages, to_added_images = _use_options_split_page_by_image(image_file_paths)
        else:
            to_added_pages, to_added_images = _use_options_no_split_page(image_file_paths)
        
        page_links = [
            epub.Link(
                href=page.file_name,
                uid=page.id,
                title=page.title
            )
            for page in to_added_pages
        ]
        epub_spines = [
            page
            for page in to_added_pages
        ]


        for page in to_added_pages:
            epub_spines += [page]
            ebook.add_item(page)

        for image in to_added_images:
            ebook.add_item(image)


        # c1 = epub.EpubHtml(title="Intro", file_name="chap_01.xhtml", lang="hr")
        # c1.content = (
        #     "<h1>Intro heading</h1>"
        #     "<p>Zaba je skocila u baru.</p>"
        #     '<p><img alt="[ebook logo]" src="static/ebooklib.gif"/><br/></p>'
        # )

        # # create image from the local image
        # # image_content = open("ebooklib.gif", "rb").read()
        # # img = epub.EpubImage(
        # #     uid="image_1",
        # #     file_name="static/ebooklib.gif",
        # #     media_type="image/gif",
        # #     content=image_content,
        # # )

        
        ebook.toc = (
            epub.Section(self.comic.comic_name),
            (
                epub.Section(self.name, ), 
                tuple(page_links)
            ),
        )

        ebook.add_item(ebooklib.epub.EpubNav())
        ebook.add_item(ebooklib.epub.EpubNcx())
        
        ebook.spine = ['nav', ] + epub_spines 



        return ebook
        
    

    def _get_comic_epub_dir(self):
        return '/'.join([
            self._get_data_dir(),
            self.comic.comic_name,
            'epub'
        ])


    def _build_epub_file_path(self):
        comic_data_epub_dir = self._get_comic_epub_dir()
        file_name = f'{self.comic.comic_name} - {self.name}.epub'
        return '/'.join([
            comic_data_epub_dir,
            self.chapter_type.value,
            file_name
        ])

    def export_to_epub(self):
        chapter_info = self._read_get_chapter_cache()
        if not chapter_info:
            raw_html = self._request_chapter_page_html()
            chapter_info = self._extract_info_from_html(raw_html=raw_html)
            self._cache_chapter_detail_info(chapter_info)

        print('      - Start Build Epub :', self.name)
        epub_book = self._build_epub_book(chapter_info=chapter_info)
        
        epub_file_path = self._build_epub_file_path()
        if not os.path.exists(os.path.dirname(epub_file_path)):
            os.makedirs(os.path.dirname(epub_file_path))

        ebooklib.epub.write_epub(epub_file_path, epub_book)
        print('        Finish Build Epub :', self.name)


    