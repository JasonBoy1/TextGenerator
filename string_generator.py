# -*- coding: utf-8 -*-
import os
import random
import re
import string
import requests

from bs4 import BeautifulSoup

def create_strings_from_file(filename, count):
    """
        Create all strings by reading lines in specified files
    """

    strings = []

    with open(filename, 'r', encoding="utf8") as f:
        lines = [l.strip()[0:200] for l in f.readlines()]
        if len(lines) == 0:
            raise Exception("No lines could be read in file")
        while len(strings) < count:
            if len(lines) > count - len(strings):
                strings.extend(lines[0:count - len(strings)])
            else:
                strings.extend(lines)

    return strings

def create_strings_from_dict(length, allow_variable, count, lang_dict):
    """
        Create all strings by picking X random word in the dictionnary
    """
    #lang_dict=lang_dict[0:0]+lang_dict[3:13]
    dict_len = len(lang_dict)
    strings = []
    for _ in range(0, count):
        current_string = ""
        rannum = random.randint(length-5, length) # 设置字符个数，可修改生成字符的个数
        count1=count2=count3=0
        textnum = 0
        textnum_last = 0
        for _ in range(0, rannum if allow_variable else length):
            #------ 修改：不连续出现两个：：或两个// ---------------------------------
            #if ((textnum_last==0 & textnum==0)|(textnum_last==2 & textnum==2)):
            #    textnum = random.randrange(1, dict_len, 2)
            #------ 修改：不连续出现两个：：或两个 //---------------------------------
            #This method restricts the rank of the char(s) in the dict---2019-6-20
                            
            #restrict the times of B,D,E,the portion is about (3/16)^2*3
            
            textnum=random.randrange(0,dict_len)
            '''
            if (_ <=(rannum/2)):#前半部分不出现
               textnum=random.randrange(0,12)
            else:
               textnum=random.randrange(0,dict_len)
            if (textnum >12):
                a2=range(dict_len)
                a2=list(a2)       
                a2.append(13);a2.append(13);a2.append(14);a2.append(14);a2.append(15);a2.append(15);
                textnum=a2[random.randint(0,len(a2)-1)]
            '''        
            #New method.不连续出现':','/'
            if (((lang_dict[textnum_last]=='/\n') & (lang_dict[textnum]=='/\n'))|((lang_dict[textnum_last]==':\n') & (lang_dict[textnum]==':\n'))):
                a1=range(dict_len)
                a1=list(a1)
                a1.remove(textnum)
                textnum=a1[random.randint(0,len(a1)-1)]
            
            #限制':''/'个数

            if (lang_dict[textnum]=='/\n'):
                count1=count1+1
                if (count1>2):
                    a1=range(dict_len)
                    a1=list(a1)
                    a1.remove(textnum)
                    textnum=a1[random.randint(0,len(a1)-1)]           

            if (lang_dict[textnum]==':\n'):
                count2=count2+1
                if (count2>2):
                    a1=range(dict_len)
                    a1=list(a1)
                    a1.remove(textnum)
                    textnum=a1[random.randint(0,len(a1)-1)]
                    
            if (lang_dict[textnum]==' \n'):
                count3=count3+1
                if (count2>3):
                    a1=range(dict_len)
                    a1=list(a1)
                    a1.remove(textnum)
                    textnum=a1[random.randint(0,len(a1)-1)]                
            #New method, you can choose every char which you do not want too see it occur repeatedly 
               
                           
            # textnum = random.randrange(dict_len)
            if (textnum==dict_len-1):
                current_string += lang_dict[textnum][:]
            else:
                current_string += lang_dict[textnum][:-1]
            # current_string += ' '

            textnum_last = textnum
            textnum=random.randrange(dict_len)
           

        strings.append(current_string.lower())
    return strings
    
def create_strings_from_wikipedia(minimum_length, count, lang):
    """
        Create all string by randomly picking Wikipedia articles and taking sentences from them.
    """
    sentences = []

    while len(sentences) < count:
        # We fetch a random page
        page = requests.get('https://{}.wikipedia.org/wiki/Special:Random'.format(lang))

        soup = BeautifulSoup(page.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()

        # Only take a certain length
        lines = list(filter(
            lambda s:
                len(s.split(' ')) > minimum_length
                and not "Wikipedia" in s
                and not "wikipedia" in s,
            [
                ' '.join(re.findall(r"[\w']+", s.strip()))[0:200] for s in soup.get_text().splitlines()
            ]
        ))

        # Remove the last lines that talks about contributing
        sentences.extend(lines[0:max([1, len(lines) - 5])])

    return sentences[0:count]

def create_strings_randomly(length, allow_variable, count, let, num, sym, lang):
    """
        Create all strings by randomly sampling from a pool of characters.
    """

    # If none specified, use all three
    if True not in (let, num, sym):
        let, num, sym = True, True, True

    pool = ''
    if let:
        if lang == 'cn':
            pool += ''.join([chr(i) for i in range(19968, 40908)]) # Unicode range of CHK characters
        else:
            pool += string.ascii_letters
    if num:
        pool += "0123456789"
    if sym:
        pool += "!\"#$%&'()*+,-./:;?@[\\]^_`{|}~"

    if lang == 'cn':
        min_seq_len = 1
        max_seq_len = 2
    else:
        min_seq_len = 2
        max_seq_len = 20

    strings = []
    for _ in range(0, count):
        current_string = ""
        for _ in range(0, random.randint(1, length) if allow_variable else length):
            seq_len = random.randint(min_seq_len, max_seq_len)
            current_string += ''.join([random.choice(pool) for _ in range(seq_len)])
            current_string += ' '
        strings.append(current_string[:-1])
    return strings
