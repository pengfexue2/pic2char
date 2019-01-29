import binascii
import os
from PIL import Image
import itchat

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

def getHeadImgs():
    #通过二维码登录微信网页版
    itchat.auto_login()
    #获取微信好友信息列表
    friendList = itchat.get_friends(update=True)

    #这里会用到的微信好友信息如下： User= {'UserName': '@8238e922e8be7356b1750c306cb75768','PYQuanPin': 'TED','NickName': 'TED'}
    #获取用户个人昵称，用于之后文件夹命名、用户头像命名
    if friendList[0]['PYQuanPin']:
        user = friendList[0]['PYQuanPin']
    else:
        user = friendList[0]['NickName']

    #先读取用户本人头像，存储名为用户名称
    selfHead = "{}/{}.jpg".format(os.getcwd(),user)
    with open(selfHead,'wb') as f:
        head = itchat.get_head_img(friendList[0]['UserName'])
        f.write(head)

    #创建文件夹用于存储好友头像
    if not os.path.exists(user):
        os.mkdir(user)

    #工作路径转到新建文件夹中
    os.chdir(user)
    #获取新建文件夹路径
    userspace = os.getcwd()


    #开始读取好友头像写入新建文件夹中
    print("开始读取%d位好友头像..."%(len(friendList)-1))
    for i in range(1,len(friendList)):
        if i % 100 ==0:
            print("已读取%d位好友头像，请耐心等待~"%i)
        try:
            friendList[i]['head_img'] = itchat.get_head_img(userName=friendList[i]['UserName'])
            friendList[i]['head_img_name'] = "%s.jpg" % friendList[i]['UserName']
        except ConnectionError:
            print('Fail to get %s' % friendList[i]['UserName'])

        with open(friendList[i]['head_img_name'],'wb') as f:
            f.write(friendList[i]['head_img'])
    print("读取好友头像完毕！")

    #保存头像的文件夹路径和用户本人头像路径返回
    return user, selfHead

def head2char(workspace,user,self,outlist):

    folder = "{}\\{}".format(workspace,user)
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
                    print("有1位朋友的头像读取失败，已使用本人头像替代")  # 有些人没设置头像，就会有异常
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * eachSize, (i // 16) * 2 * eachSize))  # 拼接图片
                # 点阵处右上角图片2/4
                try:
                    img = Image.open(imgList[x2])  # 打开图片
                except IOError:
                    print("有1位朋友的头像读取失败，已使用本人头像替代")  # 有些人没设置头像，就会有异常
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * eachSize, (i // 16) * 2 * eachSize))  # 拼接图片
                # 点阵处左下角图片3/4
                try:
                    img = Image.open(imgList[x3])  # 打开图片
                except IOError:
                    print("有1位朋友的头像读取失败，已使用本人头像替代")  # 有些人没设置头像，就会有异常
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * eachSize, ((i // 16) * 2 + 1 ) * eachSize))  # 拼接图片
                # 点阵处右下角图片4/4
                try:
                    img = Image.open(imgList[x4])  # 打开图片
                except IOError:
                    print("有1位朋友的头像读取失败，已使用本人头像替代")  # 有些人没设置头像，就会有异常
                    img = Image.open(self)
                finally:
                    img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * eachSize, ((i // 16) * 2 + 1) * eachSize))  # 拼接图片
                #调整n以读取后续图片
                n= (n+4) % len(imgList)

        os.chdir(workspace)
        # 创建文件夹用于存储输出结果
        if not os.path.exists('{}_output'.format(user)):
            os.mkdir('{}_output'.format(user))
        os.chdir('{}_output'.format(user))
        #quality代表图片质量，1-100
        canvas.save('result%d.jpg'% count, quality=100)



if __name__=="__main__":
    #将想转化的字赋给字符串
    inpt = "生日快乐，事事顺心！"

    #将字转化为汉字库的点阵数据
    outlist = char2bit(inpt)

    #获取当前文件夹路径
    workspace = os.getcwd()

    #获取用户本人名称和用户本人头像路径
    user,self = getHeadImgs()

    #将头像图片按点阵拼接成单字图片
    head2char(workspace,user,self,outlist)
    print("Well done!")
