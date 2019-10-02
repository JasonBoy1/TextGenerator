# -*- coding: utf-8 -*-
import os
import cv2
import random


# from scipy import *
import numpy as np
from skimage import exposure
from PIL import ImageEnhance


from PIL import Image, ImageFilter

from computer_text_generator import ComputerTextGenerator
try:
    from handwritten_text_generator import HandwrittenTextGenerator
except ImportError as e:
    print('Missing modules for handwritten text generation.')
from background_generator import BackgroundGenerator
from distorsion_generator import DistorsionGenerator


def RGBAcrop(im=Image.new('RGBA', (100,100), (255, 255, 255, 0)), Lthreshold=100,direction=''):
    im1=im.convert('L')
    arr=np.array(im1)    

    x_left=len(arr[0]);x_right=0;y_top=len(arr);y_bottom=0                 
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if (arr[i][j]<Lthreshold):
                if (j<x_left):
                    x_left=j
                if (j>x_right):
                    x_right=j
                if (i<y_top):
                    y_top=i
                if (i>y_bottom):
                    y_bottom=i                
    
    if direction=='td':
        im2= im.crop(box=(0,y_top,im.size[0],y_bottom+1))
    elif direction=='lr':
        im2= im.crop(box=(x_left,0,x_right+1,im.size[1]))
    else:
        im2= im.crop(box=(x_left,y_top,x_right+1,y_bottom+1))
    return im2 

#定义添加椒盐噪声的函数
def SaltAndPepper(src, percetage):
    SP_NoiseImg = src
    SP_NoiseNum = int(percetage*src.size[0]*src.size[1])
    for i in range(SP_NoiseNum):
        randX = np.random.random_integers(0, src.size[0]-1)
        randY = np.random.random_integers(0, src.size[1]-1)
        addrand = int(np.random.randint(0, 100))
        dim = len(SP_NoiseImg.size)
        if dim == 2:
            if np.random.random_integers(0, 1) == 0:
                SP_NoiseImg.putpixel((randX, randY), addrand)
            else:
                SP_NoiseImg.putpixel((randX, randY), 255)
        elif dim == 3:
            if np.random.random_integers(0, 1) == 0:
                SP_NoiseImg.putpixel((randX, randY), (0, 0, 0))
                SP_NoiseImg.putpixel((randX, randY), (0, 0, 0))
                SP_NoiseImg.putpixel((randX, randY), (0, 0, 0))
            else:
                SP_NoiseImg.putpixel(randX, randY, (255, 255, 255))
                SP_NoiseImg.putpixel(randX, randY, (255, 255, 255))
                SP_NoiseImg.putpixel(randX, randY, (255, 255, 255))
    return SP_NoiseImg

#定义添加高斯噪声的函数
def addGaussianNoise(image, percetage):
    G_Noiseimg = image
    G_NoiseNum = int(percetage*image.size[0]*image.size[1])
    for i in range(G_NoiseNum):
        randX = np.random.randint(0, image.size[0]-1)
        randY = np.random.randint(0, image.size[1]-1)
        addrand = int(np.random.randint(0, 100))
        dim = len(G_Noiseimg.size)
        if dim == 2:
            G_Noiseimg.putpixel((randX, randY), addrand)
        elif dim == 3:
            G_Noiseimg.putpixel((randX, randY), (0, 0, 0))
            G_Noiseimg.putpixel((randX, randY), (0, 0, 0))
            G_Noiseimg.putpixel((randX, randY), (0, 0, 0))
    return G_Noiseimg


class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """

        cls.generate(*t)
       
    @classmethod
    def generate(cls, index, text, font, out_dir, height, extension, skewing_angle, random_skew,
                 blur, random_blur, background_type, distorsion_type, distorsion_orientation,
                 is_handwritten, name_format, width, alignment, text_color):
        image = None
      

        ##########################
        # Create picture of text #
        ##########################
        if is_handwritten:
            image = HandwrittenTextGenerator.generate(text)
        else:
            image = ComputerTextGenerator.generate(text, font, text_color, height)
        #image.show()

        # random_angle = random.randint(0-skewing_angle, skewing_angle)
        #random_angle = random.uniform(0-skewing_angle, skewing_angle)
        #angle: 50%==0,30%>0,20%<0
        flag=random.uniform(0,1)
        if (flag<0.5):
            random_angle=0
        elif (flag<0.7):
            random_angle=random.uniform(0-skewing_angle, 0)
        else :
            random_angle=random.uniform(0, skewing_angle)
            
        rotated_img = image.rotate(skewing_angle if not random_skew else random_angle, expand=1, resample=Image.BICUBIC)

        # rotated_img = image.transform(image.size, Image.AFFINE,  (1, 0.3, 0,
        #                                                           0, 1, 0))
        # image_name = '{}__{}.{}'.format(text, str(index), extension)
        # rotated_img.convert('RGB').save(os.path.join(out_dir, image_name))

        #############################
        # Apply distorsion to image #
        #############################
        if distorsion_type == 0:#0: None (Default), 1: Sine wave, 2: Cosine wave, 3: 0+1+2 , 4: Random
            distorted_img = rotated_img # Mind = blown
        elif distorsion_type == 1:
            distorted_img = DistorsionGenerator.sin(
                rotated_img,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
            )
        elif distorsion_type == 2:
            distorted_img = DistorsionGenerator.cos(
                rotated_img,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
            )
        elif distorsion_type == 3:
             ra = np.random.rand(1)
             if ra > 1/3*2:
                 distorted_img = rotated_img  # Mind = blown
             elif ra < 1/3:
                 distorted_img = DistorsionGenerator.sin(
                     rotated_img,
                     vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                     horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                 )
             else:
                 distorted_img = DistorsionGenerator.cos(
                     rotated_img,
                     vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                     horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                 )
        else:
            distorted_img = DistorsionGenerator.random(
                rotated_img,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
            )


        ##################################
        # Resize image to desired format #
        ##################################
        # if(distorted_img.size[0]==0 | distorted_img.size[1]==0):
        #     height = 3

        # scale = max(distorted_img.size[0] / 280, distorted_img.size[1] / 32)
        scale = min(width/(0.0001+distorted_img.size[0]),  float(height)/(0.0001+distorted_img.size[1]))
        # resized_img = cv2.resize(distorted_img, None, fx=scale, fy=scale)


        # new_width = int(float(distorted_img.size[0] + 1) * (float(height) / float(distorted_img.size[1] + 1)))
        # resized_img = distorted_img.resize((new_width, height - 1), Image.ANTIALIAS)

        new_width = int(scale*distorted_img.size[0])
        new_height = int(scale * distorted_img.size[1])  
        #resized_img = distorted_img.resize((new_width, new_height - 1), Image.ANTIALIAS)
        resized_img = rotated_img
        #
        #resized_img.show()
        # image_name = '{}__{}.{}'.format('out/', '1', '.jpg')
        # resized_img.convert('RGB').save(os.path.join(image_name))
        resized_img1 =resized_img.convert("L") 
        arr1=np.asarray(resized_img1)
        amount=0
        for i in range(len(arr1)):
            for j in range(len(arr1[0])):
                if (arr1[i][j]>160):
                    pass
                else:
                    amount=amount+1   
        mean1 = np.mean(arr1)*(amount)/(resized_img1.size[0]*resized_img1.size[1]) 
       
             
        background_width = width if width > 0 else new_width + 1
        #print(resized_img.size[0],resized_img.size[1])
        #############################
        # Generate background image #
        #############################
        if background_type == 0:#0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Pictures"
            background = BackgroundGenerator.gaussian_noise(height, background_width)
        elif background_type == 1:
            background = BackgroundGenerator.plain_white(height, background_width)
        elif background_type == 2:
            background = BackgroundGenerator.quasicrystal(height, background_width)
        else:
            #background = BackgroundGenerator.picture(height, background_width)
            background = BackgroundGenerator.picture(resized_img.size[1],int(max(resized_img.size[0],resized_img.size[1]*280/32)))
            background1 =background.convert("L") 
            arr2=np.asarray(background1)
            mean2 = np.mean(arr2)
            while (mean2-mean1<80):
                background = BackgroundGenerator.picture(resized_img.size[1],int(max(resized_img.size[0],resized_img.size[1]*280/32)))
                background1 =background.convert("L") 
                arr2=np.asarray(background1)
                mean2 = np.mean(arr2)
            #print(mean1,mean2)
        if mean2<120:
            arr2=np.asarray(background1)
            arr3=arr2+30
            background=Image.fromarray(arr3)

            #print (mean1,mean2,text)
        # image_name = '{}__{}.{}'.format('out/', '1', '.jpg')
        # background.convert('RGB').save(os.path.join(image_name))
        #############################
        # Place text with alignment #
        #############################
        #print(len(text))
        background.paste(resized_img, (int((background.size[0]-resized_img.size[0])/2), 0), resized_img)
        #background.show()
        #print(x_left,y_top,x_right,y_bottom)
        #background.show()                   
        #background = background.resize((width, height),Image.ANTIALIAS)
              
        new_text_width, _ = resized_img.size
        '''
        if alignment == 0:#0: left, 1: center, 2: right , 3:随机
            background.paste(resized_img, (2, 0), resized_img)
            # background.paste(resized_img, (5, 5), resized_img)
        elif alignment == 1:
            background.paste(resized_img, (int(background_width / 2 - new_text_width / 2), 0), resized_img)

        elif alignment == 2:
            background.paste(resized_img, (background_width - new_text_width+1, 0), resized_img)

        else:
            if np.random.rand(1) > 1/3*2:
                background.paste(resized_img, (2, 2), resized_img)
            elif np.random.rand(1) < 1/3:
                background.paste(resized_img, (int(background_width / 2 - new_text_width / 2), 2), resized_img)
            else:
                background.paste(resized_img, (background_width - new_text_width+1, 2), resized_img)
        '''
        # image_name = '{}_{}.{}'.format('out/', '2', '.jpg')
        # background.convert('RGB').save(os.path.join(image_name))


        #final_image.show()
        #####################################
        # Generate name for resulting image #
        #####################################
        '''text1=list(text) #字符串转列表再转字符串       
        for i,c in enumerate(text1):
            if ((c==':')|(c==' ')):
                text1.remove(c)
        for i,c in enumerate(text1):
            if (c=='/'):
                text1[i]='!'
        text1="".join(text1)
        '''    
        if name_format == 0:
        #0: [TEXT]_[ID].[EXT], 1: [ID]_[TEXT].[EXT] 2: [ID].[EXT] + one file labels.txt containing id-to-label mappings
            # -------修改文件名字--------#
            # text_name = text.replace('/', 'A')
            text_name = text.replace(':', '')
            text_name = text_name.replace(' ', '')
            text_name = text_name.replace('/', '!')
            text_name = text_name.replace('O', '0')
            text_name = text_name.replace('有', 'A')
            text_name = text_name.replace('机', 'B')
            text_name = text_name.replace('码', 'C')

            image_name = '{}_{}.{}'.format(text_name, str(index), extension)
        elif name_format == 1:
            image_name = '{}_{}.{}'.format(str(index), text, extension)
        elif name_format == 2:
            image_name = '{}.{}'.format(str(index), extension)
        elif name_format == 3:
            text_name = text.replace(':', '')
            text_name = text_name.replace(' ', '')
            text_name = text_name.replace('/', '!')
            text_name = text_name.replace('O', '0')
            image_name = '{}.{}'.format(text_name, extension)        
        else:
            print('{} is not a valid name format. Using default.'.format(name_format))
            image_name = '{}_{}.{}'.format(text, str(index), extension)
            
        #background.convert('RGB').save(os.path.join(out_dir,image_name1)) 
        #resized_img.convert('RGB').save(os.path.join(out_dir,image_name2)) 
        ##################################
        # Apply gaussian blur #
        ##################################
        #print(image_name)
        final_image = background
        '''filter(
            ImageFilter.GaussianBlur(
                radius=(blur if not random_blur else random.randint(0, blur))
            )
        )
        
        #####################################
        # 添加：随机噪声+图像亮度微调 #
        #####################################
        rand = np.random.rand(1)
        if rand > 0.7:# 亮度增强
            brightness = np.random.rand(1)+0.6
            if brightness > 1.1:
                brightness = 1.1
            enh_bri = ImageEnhance.Brightness(final_image)
            final_image = enh_bri.enhance(brightness)
        # elif np.random.rand(1) > 0.7:  # 色度增强
        #     enh_col = ImageEnhance.Color(final_image)
        #     color = np.random.rand(1)*1.5
        #     final_image = enh_col.enhance(color)
        # elif np.random.rand(1) > 0.6:  # 对比度增强
        #     enh_con = ImageEnhance.Contrast(final_image)
        #     contrast = np.random.rand(1)*1.2+0.5
        #     final_image = enh_con.enhance(contrast)
        elif (rand < 0.7) & (rand > 0.3):   # 锐度增强
            enh_sha = ImageEnhance.Sharpness(final_image)
            sharpness = np.random.rand(1)*3
            final_image = enh_sha.enhance(sharpness)
        else:
            rand1 = np.random.rand(1)
            if rand1 > 0.7:
                percentrand1 = np.random.rand(1) * 0.002 
                final_image = addGaussianNoise(final_image, percentrand1)  # 添加高斯噪声
            elif rand1 < 0.3:
                percentrand2 = np.random.rand(1) * 0.004 
                final_image = SaltAndPepper(final_image, percentrand2)  # 添加椒盐噪声
        #final_image.show()
        '''
   
   
        # Save the image
        # resize 图像
        
        flag1=random.uniform(0,1)
        if (flag1 < 0.2):
            final_image1 = final_image

        elif (flag1 < 0.6):
            final_image1 = RGBAcrop(final_image,Lthreshold=mean2-30,direction='')
            
        elif (flag1 < 0.8):
            final_image1 = RGBAcrop(final_image,Lthreshold=mean2-30,direction='td')
  
        else :
            final_image1 = RGBAcrop(final_image,Lthreshold=mean2-30,direction='lr')
        final_image1 = final_image1.resize((width, height),Image.ANTIALIAS)
        pic3 =final_image1.convert("L") 
        arr3=np.asarray(pic3)
        mean3 = np.mean(arr3)
        if mean3<10:  
            final_image = final_image.resize((width, height),Image.ANTIALIAS)
        else:
            final_image = final_image1.resize((width, height),Image.ANTIALIAS)
        final_image.convert("RGB").save(os.path.join(out_dir, image_name),quality=100)
        

