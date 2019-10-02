# -*- coding: utf-8 -*-
import cv2
import math
import random
import os
import numpy as np
import math
from IPython import embed
from PIL import Image, ImageFont, ImageDraw, ImageFilter
key =3

def bleach(im,gray,*args):
    global key
    global fill
    temp_arr = np.array(im)
    temp_arr1=temp_arr            
    H,W =len(temp_arr),len(temp_arr[0])
    for c in args:
        slide = random.randint(10,25)*key
        bound1 = random.randint(0,3)*key
        bound2 = random.randint(0,3)*key
        
        if c == 'l':
            h1,h2,w1,w2  = H-25*key, H, 0 , int(W/3)
        elif c =='ls':
            h1,h2,w1,w2  = H-slide, H-slide+7*key+bound2, 0 , int(W/3)
        elif c == 'lt':
            h1,h2,w1,w2  = H-25*key, H-15*key, 0 , int(W/3)
        elif c == 'lb':
            h1,h2,w1,w2  = H-10*key, H, 0 , int(W/3)
        
        elif c == 'r':
            h1,h2,w1,w2  = H-28*key, H, int(2*W/3)-1*key, W
        elif c == 'rs':
            h1,h2,w1,w2  = H-slide, H-slide+7*key+bound1, int(2*W/3)-1*key, W
        elif c == 'rt':
            h1,h2,w1,w2  = H-25*key, H-15*key, int(2*W/3)-1*key, W
        elif c == 'rb':
            h1,h2,w1,w2  = H-10*key, H, int(2*W/3)-1*key, W
        
        elif c == 'm':
            h1,h2,w1,w2  = H-28*key, H, 0, int(W/3)+4*key
        elif c == 'ms':
            h1,h2,w1,w2  = H-slide, H-slide+7*key, 0, int(W/3)+4*key
        elif c == 'mt':
            h1,h2,w1,w2  = H-25*key, H-15*key, 0, int(W/3)+4*key
        elif c == 'mb':
            h1,h2,w1,w2  = H-10*key, H, 0, int(W/3)+4*key

        a, b = (w2-w1)/2, (h2-h1)/2
        for i in range(h1,h2):#纵向h1,h2
            for j in range(w1,w2):#水平w1,w2
                if temp_arr[i][j][3]==0:
                    pass
                elif ((j-(w1+w2)/2)/a)**2>1:
                    pass
                else:
                    temp_arr[i][j][0]=temp_arr1[i][j][0]+int(gray*key*(1-(((j-(w1+w2)/2)/a)**2)))#gray
                    temp_arr[i][j][1]=temp_arr1[i][j][1]+int(gray*key*(1-(((j-(w1+w2)/2)/a)**2)))#gray
                    temp_arr[i][j][2]=temp_arr1[i][j][2]+int(gray*key*(1-(((j-(w1+w2)/2)/a)**2)))#gray
    im1=Image.fromarray(temp_arr)
    return im1
    
             
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


class ComputerTextGenerator(object):

    @classmethod
    def generate(cls, text, font, text_color, font_size):#text==string, the list of all the strs in one output
        global key
        font_size=int(key*font_size)
        image_font = ImageFont.truetype(font=font, size=font_size)
        a=random.uniform(0,1)
        if a<0.7:
            fill = random.randint(text_color[0],80)
        elif a>0.7:     
            fill = random.randint(80,text_color[-1])
        text_width, text_height = image_font.getsize(text)
      
        width = 0
        height = 0
        chars_size = []
        y_offset = 10 ** 5
        #print ("y_offset", y_offset)

        char_space_width = []
        for i, c in enumerate(text):#i(int)==index of text; c(str)== item of text
            size = image_font.getsize(c)#size==(w,h)of the font
 
            chars_size.append(size)#store every length of the strings in text

            is_random_space = 1 # 是否随机字符间距
            if is_random_space == 1:
                char_space_width.append(int(np.random.uniform(2, 10)))#store the numbers of the spaces(integer)
                if i == len(text)-1:
                    width += size[0]
                else:
                    width += size[0] + char_space_width[i]
            else:
                width += size[0]


            # set max char height as word height
            if size[1] > height:
                height = size[1]
  
            # Min chars y offset as word y offset
            # Assume only y offset
            c_offset = image_font.getoffset(c)
            if c_offset[1] < y_offset:
                y_offset = c_offset[1]
            if c=='\\':
                width+=4*key
            
        # char_space_width = int(height * np.random.uniform(self.cfg.random_space.min, self.cfg.random_space.max))
        # char_space_width = int(height * np.random.uniform(-0.1, 0.7))
        # width += (char_space_width * (len(text)))

        text_x = 0  # int((text_width - width) / 2)
        text_y = int((text_height - height) / 2)

        c_x = text_x#the start point of the text,without the background,the characters are exactly stand at the start point and end point.
        # if c_x < 0:
        #     c_x = 0
        c_y = text_y
        # if char_space_width > 0:
        #     text_width += char_space_width*(2+len(text))+3
        # else:
        #     text_width += 3

        txt_img = Image.new('RGBA', (width, text_height), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)

        txt_img1 = Image.new('RGBA', (width, text_height), (255, 255, 255, 0))        

        
        flag1=random.randint(1,3)
        # 将字符一个一个画到图像上 #

        for i, c in enumerate(text):
            # self.draw_text_wrapper(draw, c, c_x, c_y - y_offset, font, word_color, force_text_border)
            txt_draw.text((c_x, 0), c, fill=(fill, fill, fill), font=image_font)
              
            width_1=chars_size[i][0]+char_space_width[i]
            
            txt_imgtemp = Image.new('RGBA', (width_1, text_height), (255, 255, 255, 0))#generate image by character
            txt_draw1 = ImageDraw.Draw(txt_imgtemp)
            txt_draw1.text((0, 0), c, fill=(fill, fill, fill,255), font=image_font)
            
            
            
            if fill<80:
                
                if c=='1':
                    if random.uniform(0,1)<0.5:
                        txt_imgtemp=bleach(txt_imgtemp,30,'l','r')
                    
                        
            if random.uniform(0,1)<0.1:
                img=txt_imgtemp.convert("L")
            
                arr=np.array(txt_imgtemp)
            
                arr1=np.array(img)
            
                for i in range(len(arr1)):
                    for j in range(len(arr1[0])):
                        arr1[i][j]=int(255-arr1[i][j])
            
                img=Image.fromarray(arr1)
          
           
                img = cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
                kernel=np.ones((6,6),np.uint8)                       
                dilation = cv2.dilate(img,kernel,iterations = 1)#膨胀后的矩阵
                #print(dilation)
                imd=Image.fromarray(dilation)
                dilation=np.array(imd)
                img=cv2.cvtColor(np.array(dilation),cv2.COLOR_RGB2BGR)
                #cv2.imshow('image',img)        
                #cv2.waitKey(0)                                              
                #txt_imgtemp.show()
            
                #Image.fromarray(dilation).convert("RGB").show() 
                dilation1=255-dilation
            
                #Image.fromarray(dilation1).convert("RGB").show()  
            
                #print(np.max(dilation))
                for i in range(len(dilation1)):
                    for j in range(len(dilation1[0])):
                    
                        if dilation1[i][j][1]<130:
                        
                            arr[i][j][0]=dilation1[i][j][0]
                            arr[i][j][1]=dilation1[i][j][1]
                            arr[i][j][2]=dilation1[i][j][2]
                            arr[i][j][3]=255
                       
                        else:  
                            pass
           
                #txt_imgtemp.show()  
                txt_imgtemp=Image.fromarray(arr)        
                #txt_imgtemp.show()                    
                #print(type(txt_imgtemp))
            
            '''if (c=='/'):
            
                #width=width+4  #for'\\'
                #width_1=width_1+4
                #txt_draw1.text((4, 0), c, fill=(fill, fill, fill), font=image_font)

                txt_draw1.line([0,0,width_1,0],fill=255,width=35*key)#up_line
                txt_draw1.line([0,text_height,width_1,text_height],fill=255,width=8*key)#down_line
                txt_imgtemp.show()
            
            
            


                if (flag1==1):#random stretch
                height_1=math.ceil(text_height*1.5)
                txt_imgtemp = txt_imgtemp.resize((width_1, height_1),Image.BILINEAR)
                txt_imgtemp = txt_imgtemp.crop(box=(0,height_1-text_height,width_1, height_1))            
               
                if ((flag1==2)):           
                    if  i == 0:
                        txt_draw1.line([0,0,0,text_height],fill=(201,)*4,width=7)#left_line
                    elif  i == len(text)-1:                
                        txt_draw1.line([width_1,0,width_1,text_height],fill=(201,)*4,width=10)#right_line
            '''
            
            #txt_imgtemp.show()
            
            
            txt_img1.paste(txt_imgtemp,(c_x,0))
    
            

            c_x += (width_1)


        
        # image_name = '{}__{}.{}'.format('out/img1/', '1', '.jpg')
        #txt_img.convert('RGB').save(os.path.join(image_name))

        #txt_img.show()
        #txt_img1.show()
          
        #background.show()                 
        #txt_img2 = RGBAcrop(txt_img1)
        txt_img2=txt_img1.resize((280,32),Image.ANTIALIAS)
        #txt_img2.show()
        
        return txt_img2

