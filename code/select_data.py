from rinex_selector import rinex_selector

path = r'C:\Users\pve_win10_1\Desktop\2020-03-25\data\生成数据'


svs = []
for x in range(1,33,1):
    if x<10: 
        svs.append('G0'+str(x)) 
    else: 
        svs.append('G'+str(x))
#del svs
#svs = ['G31','G32']
boy = rinex_selector(path,svs)
#boy.door(path)
boy.sort(r'C:\Users\pve_win10_1\Desktop\gnss-downloader\code\db.json')
#boy.auto_run()
#boy.see('连续','G31')
#boy.see('去重','G32')
