from ftplib import FTP
import os
from tqdm import tqdm
import numpy as np
import shutil
import sys

class gps_downloader(object):
    host = "igs.gnsswhu.cn"
    product = ['sp3','clk','snx','sum','erp','cls','ssc','res','igs']
    data_path_prefix = '/pub/gps/data/daily/'
    product_path_prefix = '/pub/gps/products/'
    data = ['m.rnx','n.rnx','o.rnx','_m','_n','_o','m','n','o']
    day_in_week = None
    gps_week = None
    total = None
    #width = 50

    def ppprint(self,f,data,t):
        print(f,end=' ')
        if data:
            for temp in data:
                if data.index(temp)!= (len(data)-1):
                    print('{:>}'.format(temp),end='、')
                else:
                    print('{:>}'.format(temp),end='')
        else:
            if t=='f':
                temp = '无文件类型（啥也不下载）'
                print('{:>}'.format(temp),end='')
            elif t=='s':
                temp = '所有观测站'
                print('{:>}'.format(temp),end='')
            else:
                temp = '0'
                
                print('{:>}'.format(temp),end='')
            
        if t=='t':
            print(' 组数据')
        else:
            print()
        
    def change_host(self,name):
        if name=='nasa':
            self.host='cddis.nasa.gov'
            self.data_path_prefix = '/gnss/data/daily/'
            self.product_path_prefix = '/gnss/products/'

        else:
            self.host="igs.gnsswhu.cn"
            self.data_path_prefix = '/pub/gps/data/daily/'
            self.product_path_prefix = '/pub/gps/products/'
    def __init__(self, selector,save_path):
        """
        selector是一个字典，值都是列表
        filetype： sp3,clk,snx,sum,erp,cls,ssc,res
                   m_rnx,n.rnx,o.rnx,_m,_n,_o,m,n,o
        times: [start,end]
        stations: 四个字的英文，没有就空着
        """
        self.dst_file_path = save_path
        self.filetype = selector['filetype']
        self.stations = selector['stations']
        self.times = self.get_times(selector['times'])
        self.change_host(selector['source'])
        self.save_path = save_path
        self.total = len(self.times) * len(self.filetype)
        print('------------------------------------')
        print('-  欢迎使用gps数据下载All in One.  -')
        print('------------------------------------')
        print('数据源:  ',self.host)
        if len(self.times)==1:
            print('时间:     {:>}'.format(self.times[0]))
        else:
            print('时间段:   {:>}'.format(self.times[0]+'  to  '+self.times[1]))
        self.ppprint('文件类型:',self.filetype,'f')
        self.ppprint('观测站:  ',self.stations,'s')
        self.ppprint('共:      ',[self.total],'t')
        print('------------------------------------')




    def get_times(self,datas):
        times = []
        start = np.datetime64(datas[0])
        end = np.datetime64(datas[1])
        days = (end - start) / np.timedelta64(1,'D')
        #print(start,end,days)
        #解算时间点
        for i in range(int(days)+1):
            caltime = start + np.timedelta64(i,'D')
            times.append(str(caltime))
        #print(times)

        return times
    def ftp_connect(self):
        """
        连接ftp
        :return:
        """
        ftp = FTP()
        ftp.set_debuglevel(0)  # 不开启调试模式
        ftp.connect(host=self.host)  # 连接ftp
        ftp.login()  # 登录ftp
        return ftp
    def download_file(self, ftp_file_path,file_type):
        """
        从ftp下载文件到本地
        :param ftp_file_path: ftp下载文件路径
        :param dst_file_path: 本地存放路径
        :return:
        """

        buffer_size = 10240  
        ftp = self.ftp_connect()
        #print(ftp.getwelcome())  #显示登录ftp信息
        file_list = ftp.nlst(ftp_file_path)
        file_list = list(map(lambda x:x.split('/')[-1],file_list))
        download_list = self.select_file(file_list,file_type)
        write_file = None
        each_bar = tqdm(total=len(download_list))

        for file_name in download_list:
            
            write_file = os.path.join(self.save_path, file_name)
            ftp_file = os.path.join(ftp_file_path, file_name)
            #print(self.save_path)
            #print(write_file)
            #print('下载文件:',file_name,end='  ')
            
            #ftp_file = os.path.join(ftp_file_path, file_name)
            #write_file = os.path.join(dst_file_path, file_name)
            with open(write_file, "wb") as f:
                ftp.retrbinary('RETR {0}'.format(ftp_file), f.write, buffer_size)
                f.close()
            #print('ok')
            each_bar.update(1)
            del write_file
        each_bar.close()
        
        
        ftp.quit()

    def gps_filter(self,typ):
        if typ == 'n.rnx':
            return 'GN'
        elif typ == 'm.rnx':
            return 'MM'
        elif typ =='o.rnx':
            return 'MO'

        pass

    def select_file(self,file_list,file_type):
        '''
        选择文件夹内的文件
        '''
        l = []
        for name in file_list:
            if file_type in self.data:
                if '.rnx' in file_type :
                    if self.gps_filter(file_type) in name:
                        l.append(name)
                elif '_' in file_type:
                    if 'rnx' not in name:
                        l.append(name)
                else:
                    l.append(name)
            else:
                if 'igs' in file_type:
                    if 'igs' in name and 'sp3' in name and self.gps_week + self.day_in_week in name:
                        l.append(name)
                else:
                    l.append(name)
        
        return l

    def get_dataest(self,dst_type):
        if 'n' in dst_type:
            return 'n'
        elif 'm' in dst_type:
            return 'm'
        else:
            return 'o'

    def get_day_in_year(self,time):
        the_year = time[0:4]
        r = np.datetime64(time) - np.datetime64(the_year+'-01-01') 
        r = str(r+ np.timedelta64(1,'D')).split(' ')[0]
        if len(r)==1:
            r = '00'+r
        elif len(r)==2:
            r = '0' + r
        else:
            pass
        return r

    def get_gps_week(self,time):
        base = np.datetime64('1980-01-06')
        r = (np.datetime64(time) - base) / np.timedelta64(1,'W')
        zhengshu= str(r).split('.')[0]
        day = str(r%1 // 0.1428).split('.')[0]
        self.day_in_week =day
        self.gps_week = zhengshu
        #print(zhengshu,day)
        
        return zhengshu

    def get_path(self,time,dst_type):
        dst_path = None
        if dst_type in self.data:
            dataest = self.get_dataest(dst_type)
            dst_path = self.data_path_prefix + time[0:4] + r'/' + self.get_day_in_year(time) + r'/'+ time[2:4] +dataest+r'/'
        else:
            dst_path = self.product_path_prefix + self.get_gps_week(time) +r'/'

        return dst_path

    def run(self):
        '''
            运行。分析需要的数据类型，日期范围，然后调用进行下载
            对于每个时间点的每种文件类型，分析出目录，然后调用下载
        '''
        
        #input('按任意键开始下载.')
        print()
        #total_bar = tqdm(total = self.total)
        print()
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_path)  
        os.makedirs(self.save_path)
        i = 1
        for time in self.times:
            
            for dst_type in self.filetype:
                path = self.get_path(time,dst_type)
                print('正在下载{}/{}组'.format(i,self.total))
                self.download_file(path,dst_type)
                #total_bar.update(1)
                i = i+1
        #total_bar.close()
        
        
'''
if __name__ == '__main__':
    host = "igs.gnsswhu.cn"
    username = ""
    password = ""
    port = ""
    ftp_file_path = "/pub/gps/data/daily/2020/061/20n/"
    dst_file_path = "/Users/vanlu/Documents/毕业设计/代码/datas"
    ftp = FTP_OP(host=host, username=username, password=password, port=port)
    ftp.download_file(ftp_file_path=ftp_file_path, dst_file_path=dst_file_path)
'''