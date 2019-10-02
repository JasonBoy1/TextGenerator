# -*- coding: utf-8 -*-
import argparse
import os, errno
import random
import re
import string
import numpy as np
import zipfile
import time
import shutil
from PIL import Image
from tqdm import tqdm
from string_generator import (
    create_strings_from_dict,
    create_strings_from_file,
    create_strings_from_wikipedia,
    create_strings_randomly
)
from data_generator import FakeTextDataGenerator
from multiprocessing import Pool

def delete(output,lenlimit):
    filename = './'+output+'/'
    pictures = os.listdir(filename)
    for picture in tqdm(pictures):
        pic = Image.open(filename + picture)
        pic =pic.convert("L") 
        arr1=np.asarray(pic)
        mean1 = np.mean(arr1)

        if mean1<10:
            os.remove('./'+output+'/'+picture)
    pictures1 = os.listdir(filename)
    if(len(pictures1))>lenlimit:
        for i in range(lenlimit,len(pictures1)):
            os.remove('./'+output+'/'+pictures1[i])
        print('The black pics and pics after number',lenlimit,'is removed')    
    return 0


def zipf1(output):
    startdir = '/home/wwj/TextRecognitionDataGenerator/'+output  #要压缩的文件夹路径
    file_news = 'AQ'+str(time.localtime(time.time()).tm_year)+'-'+str(time.localtime(time.time()).tm_mon)+'-'+str(time.localtime(time.time()).tm_mday)+'-'+str(time.localtime(time.time()).tm_hour)+':'+str(time.localtime(time.time()).tm_min) +'.zip' # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in (os.walk(startdir)):
        fpath = dirpath.replace(startdir,'') #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in tqdm(filenames):
            z.write(os.path.join(dirpath, filename),fpath+filename)                
    z.close()    
    print('The zip file is',file_news)
    
def valid_range(s):
    if len(s.split(',')) > 2:
        raise argparse.ArgumentError("The given range is invalid, please use ?,? format.")
    return tuple([int(i) for i in s.split(',')])

# 参数设置
def parse_arguments():
    """
        Parse the command line arguments of the program.
    """

    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(# 保存图像路径
        "--output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="out",
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        nargs="?",
        help="When set, this argument uses a specified text file as source for the text",
        default=""
    )
    parser.add_argument(# 字母表 dicts
        "-l",
        "--language",
        type=str,
        nargs="?",
        help="The language to use, should be fr (French), en (English), es (Spanish), de (German), or cn (Chinese)or num (number).",
        default="MengNiuMilk"
    )
    parser.add_argument(# 生成图像数量
        "-c",
        "--count",
        type=int,
        nargs="?",
        help="The number of images to be created.",
        default=500
    )
    parser.add_argument(
        "-rs",
        "--random_sequences",
        action="store_true",
        help="Use random sequences as the source text for the generation. "
             "Set '-let','-num','-sym' to use letters/numbers/symbols. If none specified, using all three.",
        default=False
    )
    parser.add_argument(
        "-let",
        "--include_letters",
        action="store_true",
        help="Define if random sequences should contain letters. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-num",
        "--include_numbers",
        action="store_true",
        help="Define if random sequences should contain numbers. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-sym",
        "--include_symbols",
        action="store_true",
        help="Define if random sequences should contain symbols. Only works with -rs",
        default=False
    )
    parser.add_argument(# 最大字符数量
        "-w",
        "--length",
        type=int,
        nargs="?",
        help="Define how many words should be included in each generated sample. If the text source is Wikipedia, this is the MINIMUM length",
        default=23
    )
    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Define if the produced string will have variable word count (with --length being the maximum)",
        default=True
    )
    parser.add_argument(# 图像高度
        "-f",
        "--format",
        type=int,
        nargs="?",
        help="Define the height of the produced images",
        default=56,
    )
    parser.add_argument(# 图像宽度
        "-wd",
        "--width",
        type=int,
        nargs="?",
        help="Define the width of the resulting image. If not set it will be the width of the text + 10. If the width of the generated text is bigger that number will be used",
        default=560
    )
    parser.add_argument(# 线程数
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=4,
    )
    parser.add_argument(# 保存图像格式
        "-e",
        "--extension",
        type=str,
        nargs="?",
        help="Define the extension to save the image with",
        default="jpg",
    )
    parser.add_argument(# 角度参数
        "-k",
        "--skew_angle",
        type=int,
        nargs="?",
        help="Define skewing angle of the generated text. In positive degrees",
        default=3,
    )
    parser.add_argument(# 是否随机转换角度
        "-rk",
        "--random_skew",
        action="store_true",
        help="When set, the skew angle will be randomized between the value set with -k and it's opposite",
        default=True,
    )
    parser.add_argument(
        "-wk",
        "--use_wikipedia",
        action="store_true",
        help="Use Wikipedia as the source text for the generation, using this paremeter ignores -r, -n, -s",
        default=False,
    )
    parser.add_argument(# 模糊图像
        "-bl",
        "--blur",
        type=int,
        nargs="?",
        help="Apply gaussian blur to the resulting sample. Should be an integer defining the blur radius",
        default=0,
    )
    parser.add_argument(# 是否模糊图像
        "-rbl",
        "--random_blur",
        action="store_true",
        help="When set, the blur radius will be randomized between 0 and -bl.",
        default=True,
    )
    parser.add_argument(# 背景
        "-b",
        "--background",
        type=int,
        nargs="?",
        help="Define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Pictures",
        default=3,
    )
    parser.add_argument(
        "-hw",
        "--handwritten",
        action="store_true",
        help="Define if the data will be \"handwritten\" by an RNN",
    )
    parser.add_argument(# 图像名字的格式
        "-na",
        "--name_format",
        type=int,
        help="Define how the produced files will be named. "
             "0: [TEXT]_[ID].[EXT], 1: [ID]_[TEXT].[EXT] 2: [ID].[EXT] + one file labels.txt containing id-to-label mappings",
        default=0,
    )
    parser.add_argument(# 正弦波动
        "-d",
        "--distorsion",
        type=int,
        nargs="?",
        help="Define a distorsion applied to the resulting image. "
             "0: None (Default), 1: Sine wave, 2: Cosine wave, 3: 0+1+2 , 4: Random",
        default=0
    )
    parser.add_argument(# 畸变
        "-do",
        "--distorsion_orientation",
        type=int,
        nargs="?",
        help="Define the distorsion's orientation. Only used if -d is specified. "
             "0: Vertical (Up and down), 1: Horizontal (Left and Right), 2: Both",
        default=0
    )

    parser.add_argument(# 字符与背景的位置
        "-al",
        "--alignment",
        type=int,
        nargs="?",
        help="Define the alignment of the text in the image. "
             "Only used if the width parameter is set. "
             "0: left, 1: center, 2: right , 3:随机",
        default=3
    )
    parser.add_argument(
        "-tc",
        "--text_color",
        type=valid_range,
        nargs="?",
        help="Define the text's color, should be either a single integer or a range in the ?,? format.",
        default=(40,)
    )

    return parser.parse_args()

def load_dict(lang):
    """
        Read the dictionnary file and returns all words in it.
    """

    lang_dict = []
    with open(os.path.join('dicts', lang + '.txt'), 'r', encoding="utf8", errors='ignore') as d:
        lang_dict = d.readlines()
    return lang_dict

def load_fonts(lang):

    """
        Load all fonts in the fonts directories
    """
    #old method which is not effective for arbitrary directory
    '''
    if lang == 'cn':
        return [os.path.join('fonts/cn', font) for font in os.listdir('fonts/cn')]
    elif lang == 'AnQiYeast':
        return [os.path.join('fonts/AnQiYeast', font) for font in os.listdir('fonts/AnQiYeast')]
    elif lang == 'DouBenDou':
        return [os.path.join('fonts/DouBenDou', font) for font in os.listdir('fonts/DouBenDou')]
    elif lang == 'AnQiJiaoMu':
        return [os.path.join('fonts/AnQiJiaoMu', font) for font in os.listdir('fonts/AnQiJiaoMu')]
    else:
        return [os.path.join('fonts/latin', font) for font in os.listdir('fonts/latin')]#字体文件路径
    '''
#new method but need to take care of the dir_name
    path1 = os.path.join('fonts', lang)
    return [os.path.join(path1, font) for font in os.listdir(path1)]

def main():
    """
        Description: Main function
    """

    # Argument parsing
    args = parse_arguments()

    # Create the directory if it does not exist.
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Creating word list
    lang_dict = load_dict(args.language)

    # Create font (path) list
    fonts = load_fonts(args.language)
    #print (fonts)
    # Creating synthetic sentences (or word)
    strings = []

    if args.use_wikipedia:
        strings = create_strings_from_wikipedia(args.length, args.count, args.language)
    elif args.input_file != '':
        strings = create_strings_from_file(args.input_file, args.count)
    elif args.random_sequences:
        strings = create_strings_randomly(args.length, args.random, args.count,
                                          args.include_letters, args.include_numbers, args.include_symbols, args.language)
        # Set a name format compatible with special characters automatically if they are used
        if args.include_symbols or True not in (args.include_letters, args.include_numbers, args.include_symbols):
            args.name_format = 2
    else:
        strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)
    # print(strings)
    string_count = len(strings)
    # if (string_count == 0)
    #     string_count = 9


    p = Pool(args.thread_count)
    for _ in tqdm(p.imap_unordered(
        FakeTextDataGenerator.generate_from_tuple,
        zip(
            [i for i in range(0, string_count)],
            strings,
            [fonts[random.randrange(0, len(fonts))] for _ in range(0, string_count)],
            [args.output_dir] * string_count,
            [args.format] * string_count,
            [args.extension] * string_count,
            [args.skew_angle] * string_count,
            [args.random_skew] * string_count,
            [args.blur] * string_count,
            [args.random_blur] * string_count,
            [args.background] * string_count,
            [args.distorsion] * string_count,
            [args.distorsion_orientation] * string_count,
            [args.handwritten] * string_count,
            [args.name_format] * string_count,
            [args.width] * string_count,
            [args.alignment] * string_count,
            [args.text_color] * string_count
        )
    ), total=args.count):
        pass
    p.terminate()

    if args.name_format == 2:
        # Create file with filename-to-label connections
        with open(os.path.join(args.output_dir, "labels.txt"), 'w', encoding="utf8") as f:
            for i in range(string_count):
                file_name = str(i) + "." + args.extension
                f.write("{} {}\n".format(file_name, strings[i]))
    print('Scanning and deleteing the black pics')
    delete(args.output_dir,args.count)
    print('Zipping the files')
    # zipf1(args.output_dir)

if __name__ == '__main__':
    main()
    

