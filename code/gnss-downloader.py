import sys
import os
from PyQt5.QtCore import QDate,Qt

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QFileDialog

from Ui_about import Ui_About
import re
from core import gps_downloader
import json

app = QApplication(sys.argv)
def check_high_dpi():
     h = str(QApplication.desktop().screenGeometry()).split(',')[-2]
     if int(h) >= 1920:
         return True
     return False

if 'win' in sys.platform and check_high_dpi():
    from Ui_gui_high_dpi import Ui_MainWindow
else:
    from Ui_gui import Ui_MainWindow

class MyMainWindow(QMainWindow,Ui_MainWindow):
    filetype = []
    source = None
    times = []
    stations = []
    savepath = None
    types= [
        'o.rnx','n.rnx','m.rnx','_n','_m','_o','igs','igu','igr'
    ]
    choice_way = 'all'
    db = {}
    again = False
    tobec = False

    def __init__(self,parent=None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.paused = False
        now = QDate.currentDate()
        self.dateEdit_start.setDate(now.addDays(-30))
        self.dateEdit_end.setDate(now.addDays(-30))
        self.pushButton_about.clicked.connect(self.openAbout)
        self.pushButton_download.clicked.connect(self.go)
        self.pushButton_path.clicked.connect(self.select_path)
        self.pushButton_open_save_path.clicked.connect(self.open_save_path)
        self.pushButton_english.clicked.connect(self.english)
        self.pushButton_shoudong.clicked.connect(self.shoudong)
        self.pushButton_auto.clicked.connect(self.auto)
        self.pushButton_pause.clicked.connect(self.pause)
        self.red = QPalette()
        self.red.setColor(QPalette.Window,Qt.red)
        self.boxs =  [
            self.checkBox_rnx_o,
            self.checkBox_rnx_n,
            self.checkBox_rnx_m,
            self.checkBox_n,
            self.checkBox_m,
            self.checkBox_o,
            self.checkBox_igs_sp3,
            self.checkBox_igu_sp3,
            self.checkBox_igr_sp3,

        ]

        self.checkBox_rnx_n.setChecked(True)
        self.checkBox_igs_sp3.setChecked(True)
        self.savepath = os.path.join(os.getcwd(),'下载数据')
        self.label_path.setText(self.savepath)
        self.readdb()
        


    def closeEvent(self, event):
        sys.exit()




    def flush(self):
        QApplication.processEvents()


    def pause(self):
        if self.paused == False:

            self.paused = True
        else:
            self.paused = False

    def shoudong(self):
        
        self.textEdit_stations.setText('手动指定：请输入站台4字英文，空格分开，默认则选择所有观测站. <br>例如: hksl afkg')
        self.choice_way = 'shoudong'
    def auto(self):
        self.textEdit_stations.setText('自动根据卫星号选择具有最大观测时常的观测站.输入2位卫星号(01-32)，空格间隔.  例如: 01 32 31')
        self.choice_way = 'auto'
    def english(self):
        self.label.setText('Select FileType')
        self.label_2.setText('Select Time')
        self.label_5.setText('Select Stations')
        self.label_6.setText('Source Server')
        self.label_8.setText('Save Path')
        self.label_3.setText('From')
        self.label_4.setText('To')
        self.label_7.setText('武汉 is faster in China.')
        self.label_10.setText('NASA is the best.')
        self.pushButton_shoudong.setText('Input by my self.')
        self.pushButton_auto.setText('Select by gps number automanticly')
        self.pushButton_path.setText('Select Path')
        self.pushButton_download.setText('Start')
        self.pushButton_pause.setText('Pause')
        self.pushButton_open_save_path.setText('Open save path')
        self.pushButton_about.setText('About')
        self.label_info.setText('Please make your choice and click Start.')
        self.checkBox_igr_sp3.setText('igr.sp3')
        self.checkBox_igu_sp3.setText('igu.sp3')
        self.checkBox_igs_sp3.setText('igs.sp3')
        self.checkBox_rnx_m.setText('MM.rnx(3.x)')
        self.checkBox_rnx_n.setText('GN.rnx(3.x)')
        self.checkBox_rnx_o.setText('MO.rnx(3.x)')
        self.checkBox_m.setText('.m(2.x)')
        self.checkBox_n.setText('.n(2.x)')
        self.checkBox_o.setText('.o(2.x)')
        self.textEdit_stations.setText('click one of the buttons left.')
        self.radioButton_nasa.setChecked(True)
        self.setWindowTitle('GNSS-Downloader   v2.0 by Mereith.')
    def open_save_path(self):
        if not os.path.exists(self.savepath):
            os.makedirs(self.savepath)


        if 'drwin' in sys.platform:
            os.system('open "'+self.savepath+'"')
        else:
            os.startfile(self.savepath)



    def select_path(self):
        self.savepath = str(QFileDialog.getExistingDirectory(self,'选取指定文件夹'))
        self.label_path.setText(self.savepath)
        
    def openAbout(self):
        aboutWindows = MyAboutWindow()
        aboutWindows.show()
        aboutWindows.exec_()

    def get_info(self):
        if not self.get_filetype():
            return False
        self.get_source()
        self.get_stations()
        if not self.get_times():
            return False
        return True

    def get_source(self):
        if self.radioButton_wuhan.isChecked():
            self.source = 'wuhan'
        else:
            self.source = 'nasa'

    def get_times(self):
        start = self.dateEdit_start.date()
        end = self.dateEdit_end.date()
        if start > end:
            return False
        else:
            self.times.append(start.toString(Qt.ISODate))
            self.times.append(end.toString(Qt.ISODate))
            return True

    def get_stations(self):
        if self.choice_way == 'all':
            pass
        elif self.choice_way =='shoudong':
            self.shoudong_get()
        else:
            self.auto_get()

    def auto_get(self):
        text = self.textEdit_stations.toPlainText()
        svs = []
        door = re.match(r'([0-3][0-9] )+',text)
        if door:
            print(text)
            for item in text.split(' '):
                svs.append(item)
        else:
            self.show_warning('输入错误。点击继续则按照正确的部分匹配，若无，则匹配所有观测站')
            self.tobec = True
            self.pause()
        if svs:
            try:
                for item in self.search_stations(svs):
                    self.stations.append(item)
            except:
                self.show_warning('输入错误。点击继续则按照正确的部分匹配，若无，则匹配所有观测站')
                self.tobec = True
                self.pause()

    def search_stations(self,data):
        door = []
        for item in data:
            r= self.db[str(item)]
            for mmm in r:
                door.append(mmm)
        return door


    def shoudong_get(self):
        text = self.textEdit_stations.toPlainText()
        if re.match(r'([a-zA-Z]{4})+',text):
            for item in text.split(' '):
                self.stations.append(item)
        else:
            self.show_warning('输入错误。点击继续则按照正确的部分匹配，若无，则匹配所有观测站')
            self.tobec = True
            self.pause()


    def get_cheakbox_info(self,box,text):
        if box.isChecked():
            self.filetype.append(text)

    def get_filetype(self):
        for i in range(len(self.boxs)):
            self.get_cheakbox_info(self.boxs[i],self.types[i])
        if not self.filetype:
            return False
        return True
        
    def updatebar(self,now,total):
        val= int ( str(now/total*100).split('.')[0])
        self.progressBar.setValue(val)
        QApplication.processEvents()



        

    def start(self):
        #print(self.stations)
        selector = {
            'source': self.source,
            'filetype': self.filetype,
            'times': self.times,
            'stations': self.stations
        }
        #print(selector)
        #print(self.savepath)
        
        self.downloader = gps_downloader(selector,self.savepath)
        self.downloader.gui(self)
        del self.downloader

    def show_warning(self,text):
        self.label_info.setAutoFillBackground(True)
        self.label_info.setPalette(self.red)
        self.label_info.setText(text)

    def show_info(self,text):
        self.label_info.setAutoFillBackground(False)
        self.label_info.setText(text)


    def clear_cache(self):
        self.filetype = []
        self.source = None
        self.times = []
        self.stations = []
        self.downloader = None

    def readdb(self):
        try:
            f = open('./lib/db.json','r')
            self.db = json.load(f)
            print(self.db)
            f.close()
        except:
            self.show_warning('无法读取db.json文件.')
        
        

    def go(self):
        # 获取数据、检查数据、搜索、下载

        if not self.paused or self.again:
            self.clear_cache()
            if not self.get_info():
                self.show_warning('请正确选择项目再点击下载！')
            else:
                self.start()

        else:
            self.again = True
            self.clear_cache()
            self.show_info('已取消.')
            self.updatebar(0,1)
            self.pushButton_download.setText('开始下载')
            self.pushButton_pause.setText('暂停')
            self.paused = False
        

class MyAboutWindow(QDialog,Ui_About):
    def __init__(self,parent=None):
        super(MyAboutWindow,self).__init__(parent)
        self.setupUi(self)



    

mainw = MyMainWindow()
mainw.show()
if app.exec_():
    sys.exit()
#sys.exit(app.exec_())
    