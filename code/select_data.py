from rinex_selector import rinex_selector
from ftp import gps_downloader

path = r'/Users/vanlu/Documents/毕业设计/代码/testt'


selector = {
    'source':'wuhan',
    'filetype': ['igs','_n'],
    'times': ['2020-03-01','2020-03-01'],
    'stations': ['jfng']
}


dl = gps_downloader(selector=selector,save_path=path)
#print(dl.get_gps_week('2020-01-01'),dl.day_in_week)
dl.run()

svs = []
for x in range(1,33,1):
    if x<10: 
        svs.append('G0'+str(x)) 
    else: 
        svs.append('G'+str(x))
#del svs
#svs = ['G31','G32']
#boy = rinex_selector(path,svs)
#boy.auto_run()
#boy.see('连续','G31')
#boy.see('去重','G32')
