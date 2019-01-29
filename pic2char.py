import binascii
import os
from PIL import Image

def char2bit(textStr):
    KEYS = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    target = []
    global count
    count = 0
    for x in range(len(textStr)):
        text = textStr[x]
        rect_list = [] * 16
        for i in range(16):
            rect_list.append([] * 16)

        gb2312 = text.encode('gb2312')
        hex_str = binascii.b2a_hex(gb2312)
        result = str(hex_str, encoding='utf-8')
        area = eval('0x' + result[:2]) - 0xA0
        index = eval('0x' + result[2:]) - 0xA0
        offset = (94 * (area-1) + (index-1)) * 32

        font_rect = None
        with open("HZK16", "rb") as f:
            f.seek(offset)
            font_rect = f.read(32)

        for k in range(len(font_rect) // 2):
            row_list = rect_list[k]
            for j in range(2):
                for i in range(8):
                    asc = font_rect[k * 2 + j]
                    flag = asc & KEYS[i]
                    row_list.append(flag)

        output = []
        for row in rect_list:
            for i in row:
                if i:
                    output.append('1')
                    count+=1
                    #print('0', end=' ')
                else:
                    output.append('0')
                    #print('.', end=' ')
            #print()

        target.append(''.join(output))
    return target

def head2char(workspace,folder,self,outlist):
    #将工作路径转移至头像文件夹
    os.chdir(folder)
    #获取文件夹内头像列表
    imgList = os.listdir(folder)
    #获取头像图片个数
    numImages = len(imgList)
    #设置头像裁剪后尺寸
    eachSize = 100

    #变量n用于循环遍历头像图片，即当所需图片大于头像总数时，循环使用头像图片
    n=0

    #变量count用于为最终生成的单字图片编号
    count = 0

    #img = Image.open(self)

    #初始化颜色列表，用于背景着色：FFFACD黄色 #F0FFFF白  #BFEFFF 蓝  #b7facd青色 #ffe7cc浅橙色  #fbccff浅紫色 #d1ffb8淡绿 #febec0淡红 #E0EEE0灰
    colorlist = ['#FFFACD','#F0FFFF','#BFEFFF','#b7facd','#ffe7cc','#fbccff','#d1ffb8','#febec0','#E0EEE0']
    #index用来改变不同字的背景颜色
    index = 0

    #每个item对应不同字的点阵信息
    for item in outlist:

        #将工作路径转到头像所在文件夹
        os.chdir(folder)

        #新建一个带有背景色的画布，16*16点阵，每个点处填充2*2张头像图片，故长为16*2*100
        #如果想要白色背景，将colorlist[index]改为'#FFFFFF'
        canvas = Image.new('RGB', (3200, 3200), colorlist[index])  # 新建一块画布
        #index变换，用于变换背景颜色
        index = (index+1)%9

        count += 1

        #每个16*16点阵中的点，用四张100*100的头像来填充
        for i in range(16*16):
            #点阵信息为1，即代表此处要显示头像来组字
            if item[i] == "1":
                #循环读取连续的四张头像图片
                x1 = n % len(imgList)
                x2 = (n+1) % len(imgList)
                x3 = (n+2) % len(imgList)
                x4 = (n+3) % len(imgList)

                #以下四组try,将读取到的四张头像填充到画板上对应的一个点位置
                #点阵处左上角图片1/4
                try:
                    img = Image.open(imgList[x1])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * eachSize, (i // 16) * 2 * eachSize))  # 拼接图片
                # 点阵处右上角图片2/4
                try:
                    img = Image.open(imgList[x2])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * eachSize, (i // 16) * 2 * eachSize))  # 拼接图片
                # 点阵处左下角图片3/4
                try:
                    img = Image.open(imgList[x3])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * eachSize, ((i // 16) * 2 + 1 ) * eachSize))  # 拼接图片
                # 点阵处右下角图片4/4
                try:
                    img = Image.open(imgList[x4])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * eachSize, ((i // 16) * 2 + 1) * eachSize))  # 拼接图片
                #调整n以读取后续图片
                n= (n+4) % len(imgList)

        os.chdir(workspace)
        # 创建文件夹用于存储输出结果
        if not os.path.exists('{}_输出'.format(user)):
            os.mkdir('{}_输出'.format(user))
        os.chdir('{}_输出'.format(user))
        #存储将拼接后的图片，quality为图片质量，1-100,100最高
        canvas.save('result%d.jpg'% count, quality=100)



if __name__=="__main__":
    #将想转化的字赋给字符串
    inpt = "二零一九新年快乐！"

    #将字转化为汉字库的点阵数据
    outlist = char2bit(inpt)

    #获取当前文件夹路径
    workspace = os.getcwd()

    #用于拼接的图片所在文件夹名称
    user = "TED"
    #获取图片文件夹所在路径
    folder = "{}\\{}".format(workspace,user)

    #若读取图片失败，用于替代的备用图片路径
    self=workspace+"\\"+"TED.jpg"
    #运行后将生成 user_输出 文件夹
    head2char(workspace,folder,self,outlist)
    print("Well done!")
