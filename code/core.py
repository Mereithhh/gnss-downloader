from ftplib import FTP
import os
import shutil
import sys
from datetime import date,timedelta

class gps_downloader(object):
    buffer_size = 10240
    host = "igs.gnsswhu.cn"
    product = ['sp3','clk','snx','sum','erp','cls','ssc','res','igs','igu','igr']
    data_path_prefix = '/pub/gps/data/daily/'
    product_path_prefix = '/pub/gps/products/'
    data = ['m.rnx','n.rnx','o.rnx','_m','_n','_o','m','n','o']
    day_in_week = None
    gps_week = None
    total = None
    download_list = []
    save_list = []
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
            self.data_path_prefix = '/pub/gps/data/daily/'
            self.product_path_prefix = '/pub/gps/products/'

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
        self.searched = 0
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
        start = date.fromisoformat(datas[0])
        end = date.fromisoformat(datas[1])
        days = (end - start) / timedelta(days=1)
        #print(start,end,days)
        #解算时间点
        for i in range(int(days)+1):
            caltime = start + timedelta(days=1)
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

    def check_save_folder(self,path):
        #print(path)
        if not os.path.exists(path):
            os.makedirs(path)

    def download_file(self):
        """
        从ftp下载文件到本地
        """
        #bar = tqdm(total=len(self.download_list),bar_format='{desc}: 正在下载 {percentage:3.0f}%|{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}|')
        
        #print(self.download_list)
        for i in range(len(self.download_list)):
            
            with open(self.save_list[i], "wb") as f:
                self.ftp.retrbinary('RETR {0}'.format(self.download_list[i]), f.write, self.buffer_size)
                f.close()
            #bar.update(1)
        #bar.close()

    def download_file_gui(self,ui):

        ui.show_info('下载中.......共{}个文件.已下载{}个 '.format(len(self.download_list),0))
        ui.updatebar(0,1)
        for i in range(len(self.download_list)): 
            if ui.paused:
                if not ui.tobec:
                    ui.show_warning('已暂停')
                else:
                    ui.show_warning('本次观测站输入有误。点击继续则按照正确的部分匹配，若无，则匹配所有观测站')
                #ui.pushButton_download.setText('取消下载')
                while True:
                    ui.flush()
                    ui.pushButton_pause.setText('继续')
                    if not ui.paused :
                        ui.pushButton_pause.setText('暂停')
                        #ui.show_info('继续下载')
                        ui.pushButton_download.setText('开始下载')
                        break
            print(self.download_list[i])
            with open(self.save_list[i], "wb") as f:
                self.ftp.retrbinary('RETR {0}'.format(self.download_list[i]), f.write, self.buffer_size)
                f.close()
            ui.updatebar(i+1,len(self.download_list))
            ui.show_info('下载中.......共{}个文件.已下载{}个 '.format(len(self.download_list),i))
        ui.updatebar(1,1)
        ui.show_info('下载完成！共下载{}个文件.感谢使用.'.format(len(self.download_list)))



    def gps_filter(self,typ):
        if typ == 'n.rnx':
            return 'GN'
        elif typ == 'm.rnx':
            return ['MM','GM']
        elif typ =='o.rnx':
            return ['MO','GO']

        

    def check_stations(self,name):
        if self.stations:
            for item in self.stations:
                if item.upper() in name.upper():
                    return True
            return False
        else:
            return True
    def select_file(self,file_list,file_type):
        '''
        选择文件夹内的文件
        '''
        l = []
        for name in file_list:
            if file_type in self.data:
                if self.check_stations(name):
                    if '.rnx' in file_type :
                        nn = self.gps_filter(file_type)
                        if len(nn)==2:
                            if nn[0] in name:
                                l.append(name)
                            if nn[1] in name:
                                l.append(name)
                        else:
                            if nn[0] in name:
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
                elif 'igr' in file_type:
                    if 'igr' in name and 'sp3' in name and self.gps_week + self.day_in_week in name:
                        l.append(name)
                elif 'igu' in file_type:
                    if 'igu' in name and 'sp3' in name and self.gps_week + self.day_in_week in name:
                        l.append(name)
                else:
                    l.append(name)
        
        return l

    def get_dataest(self,dst_type):
        if 'rnx' in dst_type:
            if dst_type == 'n.rnx':
                return 'n'
            elif dst_type =='o.rnx':
                return 'o'
            else:
                return 'm'
        else:
            if 'm' in dst_type:
                return 'm'
            elif 'n' in dst_type:
                return 'n'
            else:
                return 'o'

    def get_day_in_year(self,time):
        the_year = time[0:4]
        r = date.fromisoformat(time) - date.fromisoformat(the_year+'-01-01') 
        r = str(r+ timedelta(days=1)).split(' ')[0]
        if len(r)==1:
            r = '00'+r
        elif len(r)==2:
            r = '0' + r
        else:
            pass
        return r

    def get_gps_week(self,time):
        base = date.fromisoformat('1980-01-06')
        r = (date.fromisoformat(time) - base) / timedelta(weeks=1)
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

    def serach_files(self,path,dst_type,time):
        
        if path[-1] == r'/':
            path = path[0:-1]
        try:
            file_list = self.ftp.nlst(path)
        except:
            return False
        file_list = list(map(lambda x:x.split('/')[-1],file_list))
        download_list = self.select_file(file_list,dst_type)
        download_list = list(set(download_list))
            
        for item in download_list:
            
            #生成保存的文件列表
            if dst_type in self.data:
                ttt='data'
            else:
                ttt='product'
            self.check_save_folder(os.path.join(self.save_path,time,ttt))
            self.save_list.append(os.path.join(self.save_path,time,ttt,item))
        for item in download_list:
            self.download_list.append(path + r'/' + item)

        return True






    def run(self):
        '''
            运行。
            先找下载的文件放到download_list里面，在下载。
        '''
        
        #input('按任意键开始下载.')
        print()
        #total_bar = tqdm(total = self.total)
        print()
        #检查文件
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_path)  
        os.makedirs(self.save_path)
        
        #连接服务器
        try:
            self.ftp = self.ftp_connect()
        except :
            print('无法连接服务器')
            sys.exit(1)
        #search_bar = tqdm(total=self.total,bar_format='正在搜索 {percentage:3.0f}%|{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}|')
        for time in self.times:
            
            for dst_type in self.filetype:
                path = self.get_path(time,dst_type)
                self.serach_files(path,dst_type,time)
                #sys.stdout.write('已找到{}个文件'.format(len(self.download_list))+'\r')
                #sys.stdout.flush()
                self.searched = len(self.download_list)
                
                #search_bar.update(1)
                #self.download_file()
                #total_bar.update(1)
        #search_bar.close()
        print('已搜索到{}个文件，开始下载'.format(len(self.download_list)))

        self.download_file()
        self.ftp.quit()
        #total_bar.close()
        
    def gui(self,ui):
        '''
        图形化运行
        '''
        self.download_list = []
        self.save_list = []
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        try:
            self.ftp = self.ftp_connect()
        except :
            ui.show_warning('无法连接ftp服务器.请尝试换源')
            return False
        i = 0
        for time in self.times:
            for dst_type in self.filetype:
                path = self.get_path(time,dst_type)
                if not self.serach_files(path,dst_type,time):
                    ui.show_warning('未发现可下载数据，请尝试更换日期')
                    return False
                ui.show_info('检索中.......')
                i = i+1
                ui.updatebar(i,self.total)
        ui.updatebar(1,1)
        ui.show_info('检索完成.......共发现{}个文件'.format(len(self.download_list)))

        self.download_file_gui(ui)
        self.ftp.quit()


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