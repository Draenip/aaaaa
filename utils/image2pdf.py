'''
原项目地址：https://github.com/salikx/image2pdf/
作者：salikx
'''

import jmcomic, os, time, yaml
from PIL import Image
from jmcomic import *
import os

def all2PDF(input_folder, pdfpath, pdfname, chap=1):
    '''
    将目录下图片转换为pdf文件
    
    args:
        input_folder: 输入目录
        pdfpath: pdf目录
        pdfname: pdf文件名
        chap: 章节数
    
    return: 
        None
    '''
    start_time = time.time()
    path = input_folder
    subdir = []
    image = []
    sources = []  # pdf格式的图

    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                subdir.append(int(entry.name))
    subdir.sort()
    subdir = [entry for entry in subdir if entry == int(chap)]
    for i in subdir:
        with os.scandir(path + "/" + str(i)) as entries:
            for entry in entries:
                if entry.is_dir():
                    print("这一级不应该有自录")
                if entry.is_file():
                    image.append(path + "/" + str(i) + "/" + entry.name)

    if "jpg" in image[0]:
        output = Image.open(image[0])
        image.pop(0)

    for file in image:
        if "jpg" in file:
            img_file = Image.open(file)
            if img_file.mode == "RGB":
                img_file = img_file.convert("RGB")
            sources.append(img_file)

    pdf_file_path = pdfpath + "/" + pdfname
    if pdf_file_path.endswith(".pdf") == False:
        pdf_file_path = pdf_file_path + ".pdf"
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
    end_time = time.time()
    run_time = end_time - start_time
    print("运行时间：%3.2f 秒" % run_time)


def downloadManga(manga):
    '''
    下载漫画
    
    args:
        manga: 漫画id
        
    return: 
        None
    '''
    config = os.path.join(os.path.dirname(__file__), "../config.yml")
    loadConfig = jmcomic.JmOption.from_file(config)
    if os.path.exists(os.path.join(os.path.dirname(__file__), "../downloads", str(manga))):    # 若已经下载直接跳过
        return
    jmcomic.download_album(manga, loadConfig)

def convertPDF(mangas):
    '''
    转换pdf文件
    
    args:
        mangas: 漫画id列表
        
    return: 
        1: 存在多p
        None: 未分多p
    '''
    config = os.path.join(os.path.dirname(__file__), "../config.yml")
    with open(config, "r", encoding="utf8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        path = data["dir_rule"]["base_dir"]
    manga_title = searchManga(mangas[0])
    with os.scandir(path) as entries:
        for entry in entries:
            if not entry.name == manga_title:
                continue
            if os.path.exists(os.path.join(os.path.join(path, entry.name+".pdf"))):
                print("文件：《%s》 已存在，跳过" % entry.name)
                break
            else:
                print("开始转换：%s " % entry.name)
                if len(os.listdir(os.path.join(path, entry.name))) > 1:
                    all2PDF(os.path.join(path, entry.name), path, f"{entry.name}-1")
                else:
                    all2PDF(os.path.join(path, entry.name), path, f"{entry.name}")
            if len(os.listdir(os.path.join(path, entry.name))) > 1:
                return 1
    return None
                    
def searchManga(id):
    '''
    搜索漫画标题
    
    args:
        id: 漫画id
        
    return: 
        漫画标题
    '''
    client = JmOption.default().new_jm_client()
    page = client.search_site(search_query=id)
    album: JmAlbumDetail = page.single_album
    return album.title


def mangaCache(id):
    '''
    检查是否缓存漫画
    
    args:
        id: 漫画id
        
    return: 
        True: 已缓存
        False: 未缓存
    '''
    title = searchManga(id)
    if os.path.exists(os.path.join(os.path.dirname(__file__), "downloads", title)):
        print("《%s》 已存在，使用缓存漫画图片进行转化" % title)
        return True
    return False