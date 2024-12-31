from glob import glob
import ebooklib.epub
import ebooklib.utils
from textual import log
import os
import re
import ebooklib
from ebooklib.utils import parse_html_string
import xml.etree.ElementTree as ET

class EbookMergerService():
    def __init__(self, opts):
        self.opts = opts

    def _extract_number_from_name(self, name):
        pattern = r'(\d+)'
        matched = re.findall(pattern, name)
        if matched:
            return matched[-1]
        return str(99999)

    def _list_epub_in_directory(self):
        
        # log("Run List =========1111========================" , dir(self))
        opts = self.opts

        # when use textual dev run 
        # it add singlequote before path 
        # cause error
        # 
        directory = opts.directory
        if directory.startswith("'") or directory.endswith("'"):
            directory = directory[1:-1]

        pattern = os.path.join(
            directory,
            '**',
            '*.epub',
        )
        # log("Found epub fiel si 111111111111s", directory, pattern)

        epub_files = glob(pattern,recursive=True)
        log("Found epub fiel si s", epub_files, directory, pattern)
        
        result  = []

        for file_path in epub_files:
            file_name = os.path.basename(file_path)
            sequence = self._extract_number_from_name(file_name)
            result += [
                {
                    'sequence': sequence,
                    'path': file_path,
                    'name': file_name
                }
            ]
        #
        # result.sort(
        #     key=lambda item: item.get('sequence')
        # )

        result = sorted(
            result,
            key=lambda item: int(item.get('sequence'))
        )
        return result

    def _merge_epub_files(self, output_path, file_paths):
        epub = ebooklib.epub

        merged_book = epub.EpubBook()

        for file_path in file_paths:
            book_name = os.path.basename(file_path)
            
            # Read the current EPUB file
            book = epub.read_epub(file_path,)

            to_replace_paths = []
            # Add the items (like chapters, content, etc.) of the current book to the merged book
            for item in book.get_items():
                # if item.get_type() == ebooklib.ITEM_DOCUMENT:  # Ensure we're adding HTML files
                    # Make a copy of the item to avoid modifying the original one

                # because my current book image is use webp
                # and ebooklib define type by extension ,
                # currently not include webp as image type yet
                # 
                is_epub_type_image = item.get_type() in [ ebooklib.ITEM_IMAGE, ebooklib.ITEM_COVER ] 
                is_media_type_image = 'image' in getattr(item, 'media_type', '')
                if is_epub_type_image or is_media_type_image:
                    old_path = item.file_name
                    new_path = f'{book_name}/{old_path}'
                    # new_path = urllib.parse.quote(new_path)
                    
                    item.id = f'{book_name}-{item.id}'
                    item.file_name = new_path
                    
                    to_replace_paths += [(old_path, new_path)]
                    merged_book.add_item(item=item)
            
            
            for item in book.get_items():
                if type(item) in [epub.EpubNav, epub.EpubNcx]:
                    continue

                if item.get_type() in  [ebooklib.ITEM_DOCUMENT]:
                    # no need replace content , just make image into folder with same folder of document is enough
                    # content = item.content.decode(errors='ignore')
                    # 
                    # for old_file_path, new_file_path in to_replace_paths:
                    #     content = content.replace(old_file_path, new_file_path)
                    #     # print("Replae ", old_file_path, ' -- > ',new_file_path)
                    # # print("NEw content/ is ", replaced_path_content)
                    # item.content = content.encode()
                    item.title = book_name
                    item.id = f'{book_name} - {item.id}'
                    item.file_name =  f'{book_name}/{item.file_name}'
                    
                    merged_book.add_item(item)                    
            
#                     print(f"""
#                           Merge Book Loop
#                           ======================
#                           {item.title}

#                         {item.id}

# {item.file_name}
#                            """)

        page_links =  [
            epub.Link(
                href=item.file_name,
                title=item.title,
                uid=item.id
            )
            for item in merged_book.get_items() 
            if item.get_type() == ebooklib.ITEM_DOCUMENT
        ]
        merged_book.toc =  (
            epub.Section('Comic Name'),
            (
                epub.Section("Sections", ), 
                tuple(page_links)
            ),
        )
        # print("Toc si ",merged_book.toc)
        # print("to Rpelace path " , to_replace_paths)
        # # Define the NCX (navigation) and TOC (table of contents) items for the merged book
        merged_book.add_item(epub.EpubNav())  # Navigation file
        merged_book.add_item(epub.EpubNcx())  # NCX file

        # # Set up the spine (the main content that will be shown when the book is read)
        merged_book.spine = ['nav'] + [item for item in merged_book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]
      

        # print("Spine is ", merged_book.spine)
        epub.write_epub(output_path, merged_book)



if __name__ == '__main__':
    # print('dpackgae' ,)
    root_path =  os.path.dirname(os.path.dirname(os.path.realpath(__file__))) 
    
    import sys
    sys.path.append(root_path)

    from cli.ebook_merger import _init_parser
    import argparse
    
    parser = argparse.ArgumentParser()
    _init_parser(parser=parser)
    opts = parser.parse_args()

    service = EbookMergerService(opts=opts)

    # sample cli : python app\ebook_merger_service.py -d  data\地狱乐

    epub_items = service._list_epub_in_directory()
    file_paths = [ item.get('path') for item in epub_items]

    print("Fiel Path is ", file_paths)

    output_file = f'{opts.output_dir}/merged.epub'
    print("Merged file is : ", output_file)
    service._merge_epub_files(output_path=output_file ,file_paths=file_paths)
