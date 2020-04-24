import sys
import os
from PyQt5.QtCore import QDate,Qt

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QFileDialog

from Ui_about import Ui_About
import re
from core import gps_downloader

app = QApplication(sys.argv)
def check_high_dpi():
     h = str(QApplication.desktop().screenGeometry()).split(',')[-2]
     if int(h) > 1920:
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
    
    '''
    手动指定：请输入站台4字英文，空格分开，默认则选择所有观测站

根据卫星号自动选择：请输入2位数字卫星号，空格分开，程序会根据卫星号自动选择具有最大观测时常的观测站

'''


    def __init__(self,parent=None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        
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

    def shoudong(self):
       
        self.textEdit_stations.setText('莫得开发,默认所有观测站')

    def auto(self):
        self.textEdit_stations.setText('莫得开发,默认所有观测站')

    def english(self):
        self.show_warning('没得开发')

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
        text = self.textEdit_stations.toPlainText()
        if re.match(r'([a-zA-Z]{4})+',text):
            for item in text.split(' '):
                self.stations.append(item)


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

    def go(self):
        # 获取数据、检查数据、搜索、下载
        self.clear_cache()
        if not self.get_info():
            self.show_warning('请正确选择项目再点击下载！')
        else:
            
            self.start()
        

class MyAboutWindow(QDialog,Ui_About):
    def __init__(self,parent=None):
        super(MyAboutWindow,self).__init__(parent)
        self.setupUi(self)



    

mainw = MyMainWindow()
mainw.show()
sys.exit(app.exec_())

    