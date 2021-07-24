from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd
import time 
import numpy as np
import tkinter as tk
from tkinter.ttk import Combobox, Frame
from tkinter import Toplevel,BOTH
from pandastable import Table
import random
'''
Created by Hao Tung Yang, if you have any question, please contact me:
mail: b07508006@ntu.edu.tw
'''
class Crawler():
    def __init__(self):
        self.periodDict = {
            "7:10": "0",
            "8:10": "1",
            "9:10": "2",
            "10:20": "3",
            "11:20": "4",
            "12:20": "5",
            "13:20": "6",
            "14:20": "7",
            "15:30": "8",
            "16:30": "9",
            "17:30": "10",
            "18:25": "A",
            "19:20": "B",
            "20:15": "C",
            "21:10": "D",
            "全選" : "" 
        }
        self.proceed = {}
        self.periodKey = list(self.periodDict.keys())
        self.crawlnum = 20
        self.week_dict = {
            "全部": "all",
            "星期一": 1,
            "星期二": 2,
            "星期三": 3,
            "星期四": 4,
            "星期五": 5,
            "星期六": 6
        }
        self.common_course_list = {
        '全部 ': 'a',
        '國文': '1',
        '外文': '2',
        '英文': '3',
        '充當': '7',
        '共同': '8',
        }
        self.class_area = {
        '全部 ': 'a',
        'A1': '1',
        'A2': '2',
        'A3': '3',
        'A4': '4',
        'A5': '5',
        'A6': '6',
        'A7': '7',
        'A8': '8',
        '新生': 'e',
        '基本': 'b'
        }
        self.other = {
        '全部課程 ': 'a',
        '密集課程': '1',
        '台科課程': '2',
        '師大課程': '3',
        }
        self.gym = {
        '無': 'X',
        '健康體適能': '1',
        '專項運動學群': '2',
        '選修體育': '4',
        '校隊班': '5',
        '進修學士班': '6',
        }
        self.wantall = {
            "符合上述條件課程": "0",
            "全部能修的課程(資料多，速度較慢)": "1",
        }
        self.week_list = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'週一':1,'週二':2,'週三':3,'週四':4,'週五':5,'週六':6}
        self.day_time_list = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'A':11,'B':12,'C':13,'D':14}
        self.day_time_list_web = {'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9','10':'E','A':'11','B':'12','C':'13','D':'14'}
        self.first_data= True
        self.class_info_all = []
        self.getNecessaryInfo()
        self.windows()

    def getNecessaryInfo(self):
        doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php')
        doc.encoding = 'big5'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        # ---------------------------- Find semester list ---------------------------- #
        semester_select = soup.find(id="select_sem")
        semester_list = [
            option.text for option in semester_select.find_all('option')]
        self.semester_list = semester_list
         # ---------------------------- Find department list ---------------------------- #
        dpt_select = soup.find(id="dptname")
        dpt_list = [
            option.text for option in dpt_select.find_all('option')]
        dpt_name_list = dpt_list.copy()
        dpt_id_list = dpt_list.copy()
        for i in range(len(dpt_id_list)):
            if (i==0):
                dpt_id_list[i] = '0'
            else:
                dpt_id_list[i] = str(dpt_id_list[i][:4])
        self.dpt_id_list = dpt_id_list
        for i in range(len(dpt_name_list)):
            if (i==0):
                dpt_name_list[i] = dpt_list[i]
            else:
                dpt_name_list[i] = str(dpt_list[i].strip())
        self.dpt_name_list = dpt_name_list
        dpt_dict = dict(zip(dpt_name_list, dpt_id_list))
        del dpt_dict['全部']
        temp_no = {'無': 'X'}
        temp_no.update(dpt_dict)
        self.dpt_dict = temp_no

        # ---------------------------- Find Program ---------------------------- #
        self.headers = {'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_05_ec.php',headers = self.headers)
        doc.encoding = 'big5'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        program_select = soup.find(id="ecnum")
        program_list =   {option.text.strip(): option['value']
                                for option in program_select.find_all('option')}
        temp_no = {'無': 'X'}
        temp_no.update(program_list)
        self.program_list = temp_no

        
    def crawl_all(self,target,percent,start_page = 0):
        offset = 0
        if(target == 'wantall'):
            pagenum = 500
            para = {
            "current_sem": self.semester,
            'cstype': '1',
            "csname":  self.keys.encode('big5'),
            "alltime": "no",
            "allproced": "no",
            "allsel": "yes",
            "page_cnt": str(pagenum),
            'startrec':str(start_page*pagenum),
            'coursename': self.keys.encode('big5')
            }
            para.update(self.proceed)  
            self.doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_result.php',params=para,headers = self.headers)            
        elif (target == 'department'):
            if(self.department == 'X'):
                return
            pagenum=150
            para = {
            "current_sem": self.semester,
            "dptname": self.department,
            'op':"S",
            "yearcode": '0',
            "alltime": "no",
            "allproced": "no",
            "page_cnt": "150",
            'startrec':str(start_page*pagenum),
            'coursename': self.keys.encode('big5')
            }
            para.update(self.proceed)  
            self.doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php',params=para,headers = self.headers)
        elif (target == 'department2'):
            if(self.department == 'X'):
                return
            pagenum=150
            para = {
            "current_sem": self.semester,
            "dptname": self.department2,
            'op':"S",
            "yearcode": '0',
            "alltime": "no",
            "allproced": "no",
            "page_cnt": "150",
            'startrec':str(start_page*pagenum),
            'coursename': self.keys.encode('big5')
            }
            para.update(self.proceed)  
            self.doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php',params=para,headers = self.headers)            
        elif(target=='gym'):
            if(self.gym_num == 'X'):
                return
            pagenum=15
            para = {
            "op": "S",
            "current_sem": self.semester,
            'cou_cname': self.keys.encode('big5') ,
            "tea_cname": "",
            "year_code": self.gym_num,
            "alltime": "no",
            "allproced": "no",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)              
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_09_gym.php',params=para,headers = self.headers)
        elif(target=='prog'):
            if(self.prog_num == 'X'):
                return
            pagenum=15
            para = {
            "current_sem": self.semester,
            'coursename': self.keys.encode('big5'),
            "ecnum": self.prog_num,
            "cou_cname": "",
            "tea_cname": "",
            "alltime": "no",
            "allproced": "no",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)              
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_05_ec.php',params=para,headers = self.headers)
        elif(target=='common'):
            pagenum=150
            para = {
            "current_sem": self.semester,
            'coursename': self.keys.encode('big5'),
            "cou_cname": "",
            "tea_cname": "",
            "alltime": "no",
            "allproced": "no",
            "classarea" : self.common,
            "page_cnt": "150",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)            
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_03_co.php',params=para,headers = self.headers)
            offset = 1 
        elif(target=='commoncourse'):
            pagenum=150
            para = {
            "current_sem": self.semester,
            'coursename': self.keys.encode('big5'),
            'couarea': self.common,
            "alltime": "no",
            "allproced": "no",
            "page_cnt": "150",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)            
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_01_major.php',params=para,headers = self.headers)


        self.doc.encoding = 'big5'
        self.doc= self.doc.text
        
        time.sleep(3.5+random.uniform(0.1,0.5))
        
        try:
            all_class_num = int(pd.read_html(self.doc)[6][0][1].split()[1])
            page = int(all_class_num/pagenum)
            self.class_info = pd.read_html(self.doc)[5]
        except:
            all_class_num = int(pd.read_html(self.doc)[7][0][1].split()[1])
            page = int(all_class_num/pagenum)
            self.class_info = pd.read_html(self.doc)[6] 
        if(offset==1):
            self.class_info.insert(9,'必/選修','通識', True)

        self.class_info = self.class_info.drop(self.class_info.columns[17], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[16], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[8], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[7], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[5], axis=1)
    
        unwant = []
        for item in range(len(self.class_info)-1):
            day = self.class_info[12-offset][1:].array[item]
            if any(un in self.class_info[4][1:].array[item] for un in self.unwant_list):
                unwant.append(item+1)
                continue
            if (day!=day):
                #print(self.class_info[4][1:].array[item],'no time limit')
                continue

            day1 = re.finditer(r"[\u4e00-\u9fff]*(\d+|[ABCD])(,(\d+|[ABCD]))*", day)
   
            want_class = True
            time_temp = []
            for i in day1: #會把符合格式的都抓出來

                word = re.search(r"[\u4e00-\u9fff]*", i.group())
                day = re.search(r"(\d+|[ABCD])(,(\d+|[ABCD]))*", i.group())
                if(word.group() in list(self.week_list.keys())): #確定是時間 而不適上課地點
                    class_time_arr = [int(self.day_time_list[j]) for j in day.group().split(',')]
                    if 0 in self.select_time[self.week_list[word.group()],class_time_arr]:
                        want_class = False
                        break
                    else :
                        time_temp.append([word.group(),class_time_arr])
                        
            if (want_class == False):
                unwant.append(item+1)
        self.class_info = self.class_info.drop(labels=unwant, axis=0).reset_index(drop=True)
        if(offset==1 ):
            self.class_info.iloc[0]['必/選修']='必/選修'
        headers = self.class_info.iloc[0]
        self.class_info =self.class_info.iloc[1:]
        self.class_info.columns = headers
        if (self.first_data):
            self.class_info_all = self.class_info
            self.first_data = False
        else:
            try:
                self.class_info_all = self.class_info_all.append(self.class_info,ignore_index=True)
            except:
                print(self.class_info_all.iloc[0])
                print(self.class_info.iloc[0])
        #進度條
        if(self.wantallcourse=='1'):
            self.message_label.configure(
            text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(int(100*(start_page+1)/(page+1)))))
            self.message_label.update()
        else:              
            self.message_label.configure(
            text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(int(percent+100/self.crawlnum*(start_page+1)/(page+1)))))
            self.message_label.update()    
        #搜尋迴圈
        if(start_page<page):
            start_page+=1
            self.crawl_all(start_page=start_page,percent=percent,target=target)


    def crawl_control(self):
        if (self.wantallcourse=='1'):
            self.crawl_all(target='wantall',percent=0)
            self.message_label.configure(
            text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(100)))
            self.message_label.update() 
            return
        self.crawl_all(target='department',percent=0)
        self.crawl_all(target='department2',percent=100/self.crawlnum*1)
        self.crawl_all(target='gym',percent=100/self.crawlnum*2)
        self.crawl_all(target='prog',percent=100/self.crawlnum*3)
        for c in range(11): #逐一檢查框格並搜尋
            if(self.classVariables[c].get()==1):
                self.common = list(self.class_area.values())[c]
                self.crawl_all(target='common',percent=100/self.crawlnum*(c+4))
                if(c==0):
                    break
        for c in range(6):
            if(self.commoncourseVariables[c].get()==1):
                self.common = list(self.common_course_list.values())[c]
                self.crawl_all(target='commoncourse',percent=100/self.crawlnum*(c+14))
                if(c==0):
                    break
        self.message_label.configure(
        text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(100)))
        self.message_label.update()    
        return
        # self.show_result()


    def windows(self):
        def define_layout(obj, cols=1, rows=1):
            def method(trg, col, row):
                for c in range(cols):
                    trg.columnconfigure(c, weight=1)
                for r in range(rows):
                    trg.rowconfigure(r, weight=1)

            if type(obj) == list:
                [method(trg, cols, rows) for trg in obj]
            else:
                trg = obj
                method(trg, cols, rows)
        def checkall(): #通識
            for n in range(1,len(self.class_pick)):
                if (self.classVariables[0].get()==0):
                    self.class_pick[n].deselect()
                if (self.classVariables[0].get()==1):
                    self.class_pick[n].select()
        def checkallcourse(): #共同課程
            for n in range(1,len(self.commoncourse_pick)):
                if (self.commoncourseVariables[0].get()==0):
                    self.commoncourse_pick[n].deselect()
                if (self.commoncourseVariables[0].get()==1):
                    self.commoncourse_pick[n].select()
        def checkallday(): #全選可以上課的時間
            for n in range(1,len(self.ccVariables)+1):
                if (self.ccVariables[n].get()==0):
                    for m in range(1,16):
                        self.cb[n*15+m-16].deselect()
                if (self.ccVariables[n].get()==1):
                    for m in range(1,16):
                        self.cb[n*15+m-16].select()   
        def diasble_all(event): #鎖定
            if(self.wantall[comboboxWantall.get()]=='1'):
                cur_state = 'disabled'
                self.commoncourse_pick[0].select()
                self.class_pick[0].select()
            else:
                cur_state = 'readonly'
                self.commoncourse_pick[0].deselect()
                self.class_pick[0].deselect()  
            checkallcourse()
            checkall()        
            comboboxDepartment.configure(state=cur_state)
            comboboxDepartment2.configure(state=cur_state)
            comboboxGym.configure(state=cur_state)
            comboboxProgram.configure(state=cur_state)       
        def show_all():
            self.class_info_all.to_excel('class_info.xls')
            app = TestApp(self.class_info_all)
            app.mainloop()
        def start_to_crawl():
            self.class_info = []
            self.first_data = True
            self.semester = comboboxSemester.get()
            self.wantallcourse = self.wantall[comboboxWantall.get()]
            self.department = self.dpt_dict[comboboxDepartment.get()]
            self.department2 = self.dpt_dict[comboboxDepartment2.get()]
            self.gym_num = self.gym[comboboxGym.get()]
            self.prog_num = self.program_list[comboboxProgram.get()]
            self.keys = keys.get()
            self.keys_no = keys_no.get()
            self.unwant_list = self.keys_no.split()
            self.select_time = np.zeros((7,15))
            for week_time in range(1,7):
                for class_time in range (1,16):
                    temp = week_time*15+class_time-16
                    self.select_time[week_time,class_time-1] = self.cbVariables[temp].get()
                    if(self.cbVariables[temp].get()==1):
                        self.proceed.update({'week'+str(week_time):'1'})
                        self.proceed.update({'proceed'+list(self.day_time_list_web.values())[class_time-1]:'1'})
            self.crawl_control()
            if(len(self.class_info_all)==0):
                self.message_label.configure(
                text="沒有符合條件的課程")
                self.message_label.update()                
                return
            
            show_all()
            

        window = tk.Tk()
        window.title('台大課程網搜尋小幫手')
        window.configure(background='white')
        align_mode = 'nswe'
        pad = 5

        select_width = 30
        select_height = 40
        button_width = select_width
        button_height = select_height/8
        div3 = tk.Frame(window,  width=select_width, height=select_height)
        div3_2 = tk.Frame(window,  width=select_width, height=button_height)
        div4 = tk.Frame(window,  width=button_width*3, height=button_height)
        div5 = tk.Frame(window,  width=button_width*3, height=select_height)
        div3.grid(column=0, row=0, padx=pad, pady=pad, sticky=align_mode)
        div3_2.grid(column=0, row=1, padx=pad, pady=pad, sticky=align_mode)
        div4.grid(column=1, row=1, padx=pad, pady=pad, sticky=align_mode) #,columnspan=2
        div5.grid(column=1, row=0, padx=pad, pady=pad, sticky=align_mode)
        window.update_idletasks()



        # ----------------------------------- div3 ----------------------------------- #
        textSemester = tk.Label(div3, text="學期")
        textSemester.grid(column=0, row=0, sticky=align_mode)

        comboboxSemester = Combobox(div3,
                                    values=self.semester_list,
                                    state="readonly")
        comboboxSemester.grid(column=1, row=0, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxSemester.current(0)
         # ----------------學院
        textDepartment = tk.Label(div3, text="開課系所一、二")
        textDepartment.grid(column=0, row=1, sticky=align_mode)
        comboboxDepartment = Combobox(div3,
                                    values=list(self.dpt_dict.keys()),
                                    state="readonly")
        comboboxDepartment.grid(column=1, row=1, sticky=align_mode,columnspan=3,padx=10,pady=10)
        comboboxDepartment.current(0)

        comboboxDepartment2 = Combobox(div3,
                                    values=list(self.dpt_dict.keys()),
                                    state="readonly")
        comboboxDepartment2.grid(column=4, row=1, sticky=align_mode,columnspan=3,padx=10,pady=10)
        comboboxDepartment2.current(0)
        # ---------------- 體育
        textGym = tk.Label(div3, text="體育課程")
        textGym.grid(column=0, row=3, sticky=align_mode)
        comboboxGym = Combobox(div3,
                                    values=list(self.gym.keys()),
                                    state="readonly")
        comboboxGym.grid(column=1, row=3, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxGym.current(0)
        # ---------------- 學程
        textProgram = tk.Label(div3, text="學程")
        textProgram.grid(column=0, row=4, sticky=align_mode)
        comboboxProgram = Combobox(div3,
                                    values=list(self.program_list.keys()),
                                    state="readonly")
        comboboxProgram.grid(column=1, row=4, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxProgram.current(0)
        # ---------------- 關鍵詞搜索
        textProgram = tk.Label(div3, text="課程包含關鍵詞")
        textProgram.grid(column=0, row=5, sticky=align_mode)
        keys = tk.StringVar()
        enterword = tk.Entry(div3,textvariable=keys)
        enterword.grid(column=1, row=5, sticky=align_mode,padx=10,columnspan=6,pady=10)
        # ---------------- 排除關鍵詞
        textProgram2 = tk.Label(div3, text="排除關鍵詞")
        textProgram2.grid(column=0, row=6, sticky=align_mode)
        keys_no = tk.StringVar()
        enterword2 = tk.Entry(div3,textvariable=keys_no)
        enterword2.insert (0,'專題研究 服務學習')
        enterword2.grid(column=1, row=6, sticky=align_mode,padx=10,columnspan=6,pady=10)
        # ---------------- 通識課程
        self.classVariables={}
        self.class_pick={}         
        for cl in range(len(self.class_area)):
            self.classVariables[cl] = tk.IntVar()
            if(cl==0):
                
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl],command=checkall )
                self.class_pick[cl].grid(column=cl+1, row=7, sticky="we",padx=4,pady=4)
            elif(cl>len(self.class_area)/2):
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl] )
                self.class_pick[cl].grid(column=cl+1-int(len(self.class_area)/2), row=8, sticky="we",padx=4,pady=4)
            else:
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl] )
                self.class_pick[cl].grid(column=cl+1, row=7, sticky="we",padx=4,pady=4)
        #print(self.class_pick[0],type(self.class_pick[0]))
        textFileName = tk.Label(div3 ,text="通識課程")#,font=(None, 15)
        textFileName.grid(row=7,column=0, sticky=align_mode,rowspan=2,padx=10,pady=10)

        # ---------------- 共同領域
        self.commoncourseVariables={}
        self.commoncourse_pick={}         
        for cl in range(len(self.common_course_list)):
            self.commoncourseVariables[cl] = tk.IntVar()
            if(cl==0):
                self.commoncourse_pick[cl] = tk.Checkbutton(div3, variable=self.commoncourseVariables[cl],text =list(self.common_course_list.keys())[cl],command=checkallcourse )
                self.commoncourse_pick[cl].grid(column=cl+1, row=9, sticky="we",padx=4,pady=4)
            else:
                self.commoncourse_pick[cl] = tk.Checkbutton(div3, variable=self.commoncourseVariables[cl],text =list(self.common_course_list.keys())[cl] )
                self.commoncourse_pick[cl].grid(column=cl+1, row=9, sticky="we",padx=4,pady=4)
        #print(self.class_pick[0],type(self.class_pick[0]))
        textFileName = tk.Label(div3 ,text="共同課程")#,font=(None, 15)
        textFileName.grid(row=9,column=0, sticky=align_mode,rowspan=1,padx=10,pady=10)
        # ---------------- 全部課程
        textWantall = tk.Label(div3, text="直接搜尋全部")
        textWantall.grid(column=0, row=10, sticky=align_mode,padx=10,pady=10)
        comboboxWantall = Combobox(div3,
                                    values=list(self.wantall.keys()),
                                    state="readonly")
        comboboxWantall.grid(column=1, row=10, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxWantall.current(0)
        comboboxWantall.bind("<<ComboboxSelected>>", diasble_all)
        # ----------------------------------- div3_2 ----------------------------------- #
        # ---------------- 顯示進度
        message_label = tk.Label(div3_2, bg='white',font=(None, 15))
        message_label['height'] = int(button_height)
        message_label['width'] = int(select_width)
        message_label.grid(column=0, row=0, sticky=align_mode)
        self.message_label = message_label

         # ----------------------------------- div5 ----------------------------------- #
        textFileName = tk.Label(div5, text="可以上課的時間",font=(None, 15))
        textFileName.grid(row=0, sticky=align_mode,columnspan=7)
        self.cbVariables={}
        self.ccVariables={}
        self.cb={}
        self.cc={}
        row_offset = 1
        for week_time in range(1,7):
            textFileName = tk.Label(div5, text=list(self.week_dict.keys())[week_time])
            textFileName.grid(column=week_time, row=row_offset, sticky=align_mode)
        for class_time in range(1,17):
            textFileName = tk.Label(div5, text=list(self.periodDict.values())[class_time-1]+"  "+list(self.periodDict.keys())[class_time-1])
            
            textFileName.grid(column=0, row=class_time+row_offset, sticky=align_mode)           
        for week_time in range(1,7):
            for class_time in range (1,16):
                temp = week_time*15+class_time-16
                self.cbVariables[temp] = tk.IntVar()
                self.cbVariables[temp].set (False)
                self.cb[temp] = tk.Checkbutton(div5, variable=self.cbVariables[temp])
                self.cb[temp].grid(column=week_time, row=class_time+row_offset, sticky=align_mode)
        for wt in range(1,7):
                self.ccVariables[wt] = tk.IntVar()
                self.ccVariables[wt].set (False)
                self.cc[wt] = tk.Checkbutton(div5, variable=self.ccVariables[wt],command=checkallday)
                self.cc[wt].grid(column=wt, row=16+row_offset, sticky=align_mode)
        # ----------------------------------- div4 ----------------------------------- #

        button = tk.Button(div4, text='開始搜尋', bg='green', fg='white',font=(None, 15))
        button.grid(column=0, row=0, sticky=align_mode)
        button['command'] = start_to_crawl

        # ------------------------------ Flexible layout ----------------------------- #

        window.columnconfigure(0, weight=4)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(0, weight=5)
        window.rowconfigure(1, weight=1)

        define_layout(div3_2,rows=1)
        define_layout(div3, rows=10)
        define_layout(div4)
        define_layout(div5)

        self.window = window
        window.mainloop()


class TestApp(Frame):
    
    def __init__(self,data_frame, parent=None):
        

        self.parent = parent
        Frame.__init__(self)
        self.main = Toplevel(self.master)
        self.main.geometry('800x600+200+100')
        self.main.title('搜尋結果')
        f = Frame(self.main)
        f.pack(fill=BOTH,expand=1)
        self.table = pt = Table(f, dataframe=data_frame,
                                showtoolbar=False, showstatusbar=False)
        pt.show()
        return

if __name__ == '__main__':
    crawler = Crawler()
