from bs4 import BeautifulSoup
from selenium import webdriver
import tkinter  as tk
import re
import time
import math

'''
    分析得知百度文库文章，是加载页面后通过js加载文章的，
    因此思路采用selenium+phantomjs脚本模拟浏览器并且完成js加载后
    使用beautifulsoup库对源代码进行处理，该方法需要导入selenium库并下载
    phantomjs2.1版本脚本，phantomjs.exe放在python目录下的scripts。
    难点：百度文库默认加载前三页文章有的文章不止篇幅三页，之后的文章需要通过点击继续阅读按钮ajax加载,
    并且页面有懒加载机制，即每次滑动到下一页时追加后三页的文章，删除前三页文章
    解决方案：使用phantomjs 使用js脚本通过计算滚动高度，模拟页面滚动条滚动并抓取文章
    问题：百度文库有部分需要vip才能继续阅读的文章，因为有服务器登录验证所以这类文章只能爬取前三页内容
'''
def reText(msg):
    print(msg)
    text.delete('1.0','end')
    text.insert('end',msg)

def printRes(url):
    #正则判断输入url是否为百度文库下的路径
    trueUrl = re.search(r'^https://wenku.baidu.com/view/[a-z\d]+\.html$',url)
    if not trueUrl:
        reText('输入路径不是百度文库下的路径')
        return
    
    driver = webdriver.PhantomJS()
    #driver.get(url)
    
    
    
    try:
        driver.get(url)
    except:
        reText('请求失败，请检查网络')
        #退出脚本命令行窗口
        driver.quit()
        return
    
    
    strs = u""
    #获取总页数
    soup = BeautifulSoup( driver.page_source, "html.parser")
    pageCount = soup.find( "span", class_="page-count").string
    pageCount = int(pageCount.replace('/',''))
    print(pageCount)
    #如果大于3页则点击继续阅读按钮，遍历输出结果，百度文库一次加载三页，因此遍历总页数/3次
    if pageCount>3:
        rangeCount = (int(pageCount) /3)
        rangeCount = math.ceil(rangeCount)
        print(rangeCount)
        #点击继续阅读
        driver.find_element_by_class_name('moreBtn').click()
        #程序休眠3秒，防止ajax请求网络延迟导致报错
        time.sleep(3)
        #定义兼容中文格式字符串
        for i in range(0,rangeCount):
            #通过程序运行结果分析，百度文库点击继续阅读后返回的文章显示在当前页面滚动条所处位置开始加载则第三页，因此排除第三页，所以加上3页的三分之一就是一页
            if i == 1:
                i = i + 0.3
            print(i)
            #js模拟滚动条下滑长度，一次滑动3759，即滑动三页
            js="document.body.scrollTop = %s"%(i*3759)
            driver.execute_script(js)
            time.sleep(1)
            soup = BeautifulSoup( driver.page_source, "html.parser")
            #分析发现文章存在class为ie-fix的div内
            res = soup.find_all( "div", class_="ie-fix")

            #遍历res下的p标签，并循环输出其中字符串
            if not res:
                reText('请求失败，请稍后重试')
                #退出脚本命令行窗口
                driver.quit()
            for data in res:
                d2 = data.find_all('p')
                if d2:
                    for i in d2:
                        if i.string:
                            strs += i.string
    else:
        soup = BeautifulSoup( driver.page_source, "html.parser")
        res = soup.find_all( "div", class_="ie-fix")
        if not res:
            reText('请求失败，请稍后重试')
            #退出脚本命令行窗口
            driver.quit()
        for data in res:
                d2 = data.find_all('p')
                if d2:
                    for i in d2:
                        if i.string:
                            strs += i.string
        
        
    
    
    
    

    #print(strs)
    
    #由于遍历出来的字符串包含分行符所以可以不需要处理直接输出
    reText(strs)
    #退出脚本命令行窗口
    driver.quit()
    

#视图窗口
window = tk.Tk()
window.title('百度文库文章爬虫')

var = tk.StringVar()
entry = tk.Entry( window, textvariable = var, width=80)
var.set('--请粘贴需要获取内容的百度文库文章路径到此处--')
entry.pack( side='top')

button = tk.Button( window, text='搜索', command = lambda:printRes(var.get()), width=20).pack()

text = tk.Text( window, width=80, height=50)
text.pack()



window.mainloop()



'''
测试地址：
1：url = "https://wenku.baidu.com/view/6220f3aa951ea76e58fafab069dc5022abea467a.html" 
2：url = https://wenku.baidu.com/view/2bfd1d37240c844768eaee78.html
'''




