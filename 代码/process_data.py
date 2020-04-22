from pyec import pyec,run,i_am_lazy1,table_cont

# 计算G31，G32的HKSL，JFNG两个观测站的对比相关数据
data_path1 = r'/Users/vanlu/Documents/毕业设计/观测文件/观测1'
savepath1 = r'/Users/vanlu/Documents/毕业设计/输出数据/观测1'
data = run(data_path1,sv_need=2,drawmode='single',cmpmode='sp3',display=False,savepath=savepath1)
i_am_lazy1(data,savepath=savepath1)
table_cont(savepath1)


#计算他喵的G31和G32两个卫星的12小时长时间数据
data_path2 = r'/Users/vanlu/Documents/毕业设计/观测文件/观测2'
savepath2 = r'/Users/vanlu/Documents/毕业设计/输出数据/观测2'






