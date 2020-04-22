import os
import georinex as gr
import numpy as np
import json
import sys
import shutil
import asyncio
import pymongo
from tqdm import tqdm

async def worker(each,navpath,working_svname,i,j):
    '''
    一个工具人，用来处理相关的文件
    '''
    #print(os.path.join(navpath, each))
    data = gr.load(os.path.join(navpath, each))
    times = data.sel(sv=working_svname).dropna(dim='time',how='all').time.values
    r = list(map(lambda x:str(x).split('.')[0],times))
    #sys.stdout.write('共{}个文件，正在处理{}号'.format(j,i)+'\r')
    #sys.stdout.flush()
    return r

async def main(files,navpath,working_svname,bar):
    db = {}
    #动态变量=locals()
    #nums = len(files)
    #创建人物队列
    '''
    for i in range(nums):
        工具人 = '万海波' + str(i)
        动态变量[工具人]=asyncio.create_task(worker(files[i],navpath,working_svname))
    for i in range(nums):
        工具人 = '万海波' + str(i)
        await 动态变量[工具人]
    '''
    
    for file in files:
        t = asyncio.create_task(worker(file,navpath,working_svname,files.index(file),len(files)))
        await t
        db[file] = t.result()
        bar.update(1)

    #sys.stdout.write('[{}]完成！'.format(working_svname)+'\r\n')
    #sys.stdout.flush()
    return db


class rinex_selector():
    svs = []
    navpath = None
    working_svname = None
    def __init__(self,navpath,svs):
        self.navpath = navpath
        self.svs = svs
        self.working_svname =svs[0]
        self.total = len(navpath) * len(svs)
    
    def drop_points(self,datas):
        '''
        时间信息的连续的最大时间范围相关信息
        '''
        def find_most(data):
            most = 0
            for i in range(len(data)):
                if float(data[i][2])>float(data[0][2]):
                    most = i
            return {'start': data[most][0],'end':data[most][1],'last':data[most][2]}

        db = {}
        #print('[{}]时间数据连续化'.format(self.working_svname))
        
        for name,times in datas.items():
            start_t =None
            last_t = None
            end_t = None
            间隔列表 = []
            for t in times:
                
                if not last_t:
                    last_t = t
                    start_t = t
                else:
                    #print('前面的t是：',last_t)
                    #print('当前的t是：',t)
                    if  np.datetime64(t) - np.datetime64(last_t) == np.timedelta64(7200,'s'):
                        #print('两者相差为两小时！')
                        end_t = t
                        last_t = t
                    else: #相差不是两个小时,重新赋值start，重制end
                        #print('两者相差不是两小时！')
                        if np.datetime64(start_t)<np.datetime64(end_t):
                            间隔列表.append([start_t,end_t,str(int(str(np.datetime64(end_t) - np.datetime64(start_t)).split(' ')[0])/3600)])
                        start_t = t
                        last_t = t
                
                #print('当前的t：{}  last:{}  start:{}  end:{} '.format(t,last_t,start_t,end_t))
            if np.datetime64(start_t)<np.datetime64(end_t):
                间隔列表.append([start_t,end_t,str(int(str(np.datetime64(end_t) - np.datetime64(start_t)).split(' ')[0])/3600)])   
            
            返回数据 = find_most(间隔列表)
            db[name]=  返回数据               
            返回数据['filename'] = name
            返回数据['gps']= self.working_svname
            
        self.save(db,self.working_svname+'连续时间数据.json')
        self.navdb.insert(返回数据)
        #print('[{}]完成！'.format(self.working_svname))
        return db

    def drop_same_and_contain(self,datas):
        '''
        从获取的持续时间字典中删除持续时间一毛一样的，以及包括了的
        '''
        #print('[{}]时间数据去重化'.format(self.working_svname))
        r = {}
        l = len(datas)
        keys = list(datas.keys())
        for i  in range(l):
            ok = 0
            for j in range(i+1,l,1):
                start1 = datas[keys[i]]['start']
                start2 = datas[keys[j]]['start']
                end1 = datas[keys[i]]['end']
                end2 = datas[keys[j]]['end']
                #只保证最大的
                if np.datetime64(start1)<= np.datetime64(start2) and np.datetime64(end1)>= np.datetime64(end2):
                    ok =1
                else:
                    pass
            if ok==1:
                r[keys[i]] =datas[keys[i]]
        self.save(r,self.working_svname+'去重时间数据.json')
        #print('[{}]完成！'.format(self.working_svname))
        return r

    def print_info(self,datas):
        print('共{}项数据'.format(len(datas)))
        for name in list(datas.keys()):
            print('文件名：{}\n起始时间：{}\n结束时间：{}\n最大时长：{}小时\n\n'.format(name,datas[name]['start'],datas[name]['end'],datas[name]['last']))
    
    def print_raw_info(self,datas):
        print('共{}项数据'.format(len(datas)))
        for name in list(datas.keys()):
            print('文件名：{}'.format(name))
            print('时间点：{}'.format(datas[name]))

    def save(self,data,filename):
        path = self.navpath + r'/生成数据'
        f = open(os.path.join(path,filename),mode='w',encoding='utf-8')
        f.write(json.dumps(data,indent=4))
        f.close() 


    def file_filter(self,lists):
        r = []
        for item in lists:
            if 'rnx' in item:
                r.append(item)
        return r
    def get_nav_time_raw_info(self):
        db = {}
        files = os.listdir(self.navpath)
        #print('[{}]获取数据并提取时间'.format(self.working_svname))

        door = self.file_filter(files)
        #print(door)
        db = asyncio.run(main(door,self.navpath,self.working_svname,self.bar))
        
        self.save(db,self.working_svname+'原始时间数据.json')
        #print('[{}]完成！'.format(self.working_svname))
        #sys.stdout.flush()
        return db


    def next(self):
        if self.working_svname == self.svs[len(self.svs)-1]:
            return False
        else:
            self.working_svname = self.svs(self.svs.index(self.working_svname)+1)
            return True

    def see(self,typ,svname):
        '''
        查看你想要的数据
        typ:   
            原始:原始的时间点数据
            连续:去离散化的时间点数据
            去重:去重复和折叠的时间点数据
        svname:
            想看的卫星号
        '''
        filename1 = os.path.join(self.navpath+r'/生成数据/',svname + '原始时间数据.json')
        filename2 = os.path.join(self.navpath+r'/生成数据/',svname + '连续时间数据.json')
        filename3 = os.path.join(self.navpath+r'/生成数据/',svname + '去重时间数据.json')
        if typ=='连续':
            self.print_info(json.load(open(filename2,'r')))
        elif typ=='去重':
            self.print_info(json.load(open(filename3,'r')))
        elif typ=='原始':
            self.print_raw_info(json.load(open(filename1,'r')))
        else:
            print('请输入正确的数据类型')

    def show_info(self):
        print('------------------------------------')
        print('-  欢迎使用星历数据处理All in One. -')
        print('------------------------------------')
    def auto_run(self):
        '''
        基于查询和处理分开的哲学，可以先处理一下数据，然后再单独的查看
        hhhh直接存储到mongodb上算了。
        
        '''
        self.bar = tqdm(total=self.total)
        self.navdb = pymongo.MongoClient(host='localhost',port=27017).gps.nav
        self.navdb.drop()
        self.show_info()
        print('需要处理{}个卫星，{}个文件，共{}项.'.format(len(self.svs),len(self.navpath),self.total))
        print()
        print()
        path = self.navpath + r'/生成数据'
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            os.mkdir(path)
        #print('需要处理的卫星号:{}'.format(self.svs))
        for sv in self.svs:
            self.working_svname = sv
            self.drop_same_and_contain(self.drop_points(self.get_nav_time_raw_info()))
        self.bar.close()
        print('[完成]相关数据保存在数据库以及:{}中.'.format(self.navpath))
        

            

