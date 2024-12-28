# Manhuagui Comic Downloader

As it name , use for download comic from [manhuagui](https://www.manhuagui.com)


## Setup 

```bash
pip install -r requirements.txt
```
or 
```bash
# conda import environment
# [manhuagui] is environment , you can type what you want 
conda env create --name manhuagui --file=conda-environments.yaml
conda activate manhuagui
```

## Usage

Help :

    usage: python main.py [-h] -i COMIC_ID [--include-volume [INCLUDE_VOLUME]] [--include-extra [INCLUDE_EXTRA]] [--include-episode [INCLUDE_EPISODE]] [--include-undefined [INCLUDE_UNDEFINED]]  

    Manhuagui Comic Downloader

    options:
    -h, --help            show this help message and exit
    -i, --comic-id COMIC_ID
                            manhuagui comic id
    --include-volume [INCLUDE_VOLUME]
                            Download Volume
    --include-extra [INCLUDE_EXTRA]
                            Download Extra
    --include-episode [INCLUDE_EPISODE]
                            Download Episode
    --include-undefined [INCLUDE_UNDEFINED]
                            Download Undefined Type 


```bash
python main.py -i [comic_id] --include-volume
```

Note : 

    You need to include **--include-volume** / **--include-extra** / ...  to download comic
    if you not include these arguments , 
    the program may not download anything

    for make no too heavy on manhuagui 
    so we should just download what we want only

    when you download VOLUME , 
    there no need to download EPISODE anymore
    this is what i thinking


## LICENSE

MIT

## Credit 

<h1>Thank to :</h1>

    Project : manhuagui : https://github.com/kimklai/manhuagui

    I copy most code from here for 
    - Extract Page Detail from manhuagui page
    - Request Download Image ( with set referer to make download no 403 forbidden )

    As i have other requirement , so i cannot commit and update on current repository

.

    Project : manhuagui.py https://github.com/chazeon/manhuagui.py
    as above project , forked from this repository

