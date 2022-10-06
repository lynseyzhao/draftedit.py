import sqlite3
import pandas as pd
import wx, wx.grid
from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from snapshot_selenium import snapshot
from pyecharts.render import make_snapshot

# columns
columns = ['CAMIS', 'DBA', 'BORO', 'BUILDING', 'STREET', 'ZIPCODE', 'PHONE', 'CUISINE_DESCRIPTION', 'INSPECTION_DATE', 'ACTION', 'VIOLATION_CODE', 'VIOLATION_DESCRIPTION', 'CRITICAL_FLAG', 'SCORE', 'GRADE', 'GRADE_DATE', 'RECORD_DATE', 'INSPECTION_TYPE']
rows = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
# conect with dataset
con = sqlite3.connect('NYC_Restaurant.db')
# cursor
cur = con.cursor()

start = ''
end = ''

# creat table
def create_table(cur):
    try:
        # sql read
        with open('create_table.sql', 'r') as f:
            sql = f.read()
        # execute
        cur.execute(sql)
        print('DatasetCompleted！')
    except:
        print('DataExist！')

# table insert
def insert_table(cur, con):
    try:

        sql = 'select * from NYC_Restaurant_Inspections'
        cur.execute(sql)
        # result
        res = cur.fetchall()
        if len(res) > 0:
            print('DataAlreadyExist！')
        else:

            data = pd.read_csv('DOHMH_New_York_City_Restaurant_Inspection_Results.csv')

            data.to_sql('NYC_Restaurant_Inspections', con=con, if_exists='replace', index=False)
            print('DataInserted！')
    except:
        print('Not Exist！')


# inheritied frame
class MyGridTable(wx.grid.GridTableBase):
    def __init__(self, sql):
        super().__init__()
        self.sql = sql
        cur.execute(self.sql)
        self.data = cur.fetchall()
        self.colLabels = columns
    def GetNumberRows(self):
        return len(self.data)
    def GetNumberCols(self):
        return len(self.colLabels)
    def GetValue(self, row, col):
        return self.data[row][col]
    def GetColLabelValue(self, col):
        return self.colLabels[col]

# Button1
def fun1(event):
    # Close main window
    global mainWindow
    # close main window
    mainWindow.Close()
    # class define
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initialsql
            self.sql = "select * from NYC_Restaurant_Inspections limit 20"
            # define panel
            self.panel = wx.Panel(self)
            # define component
            self.mainButton = wx.Button(self.panel, label='Time', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30), name="file1")
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30), name="file2")
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            self.grid = wx.grid.Grid(parent=self.panel)
            # layout(sizer)
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.VERTICAL)
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.get_set()
            # buttonbind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, self.search)

        def get_set(self):
            # tableset
            table = MyGridTable(self.sql)
            self.grid.SetTable(table, True)
            self.grid.AutoSize()
            # layout size
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer1, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.sizer3, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            self.sizer5.Add(self.grid, flag=wx.ALL, border=5)
            # layout
            self.panel.SetSizer(self.sizer5)

        def search(self, event):
            if len(self.file1.GetValue()) == 10 and len(self.file2.GetValue()) == 10 and len(
                    self.file1.GetValue().replace('/', '')) == 8 and len(self.file2.GetValue().replace('/', '')) == 8:
                global start, end
                start = self.file1.GetValue().split('/')[2] + self.file1.GetValue().split('/')[0] + \
                        self.file1.GetValue().split('/')[1]
                end = self.file2.GetValue().split('/')[2] + self.file2.GetValue().split('/')[0] + \
                      self.file2.GetValue().split('/')[1]
                self.sql = "select * from NYC_Restaurant_Inspections where substr(INSPECTION_DATE,7,4) || substr(INSPECTION_DATE,1,2) || substr(INSPECTION_DATE,4,2) between '{}' and '{}'".format(
                    start, end)
                cur.execute(self.sql)
                self.data = cur.fetchall()

                self.page = 0

                self.get_set(self.data[self.page: self.page + 20])
            else:
                self.text1.Destroy()
                self.text2.Destroy()
                self.file1.Destroy()
                self.file2.Destroy()
                self.searchButton.Destroy()
                self.grid.Destroy()
                self.backButton.Destroy()
                self.nextButton.Destroy()
                self.text4 = wx.StaticText(self.panel, label='No Found', size=(200, 100))

                self.panel.SetSizer(self.text4)
# page filp
        def get_page(self, event, page):
            if page == -1 and self.page == 0:
                pass
            elif page == 1 and int(self.index[-1]) >= len(self.data):
                pass
            else:
                self.page += page
                self.index = list(map(lambda x: str(int(x) + page * 20), self.index))
                # self.text = wx.StaticText(self.panel, label=str(self.page), size=(10, 20))
                self.get_set(self.data[self.page * 20: self.page * 20 + 20])

    # window
    window = window()
    # window.show
    window.Show()
    # mainwindow
    mainWindow = window

# button2
def fun2(event):
    # close window
    global mainWindow
    # close window
    mainWindow.Close()
    # class window
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initialdata
            self.sql = "select * from NYC_Restaurant_Inspections limit 20"
            cur.execute(self.sql)
            self.data = cur.fetchall()
            # panel
            self.panel = wx.Panel(self)
            # component
            self.mainButton = wx.Button(self.panel, label='Violation Distribution', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30))
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30))
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            # layout size
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.VERTICAL)
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer1, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.sizer3, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            # layout
            self.panel.SetSizer(self.sizer5)
            # buttonbind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, self.search)

        def search(self, event):
            if len(self.file1.GetValue()) == 10 and len(self.file2.GetValue()) == 10 and len(self.file1.GetValue().replace('/', '')) == 8 and len(self.file2.GetValue().replace('/', '')) == 8:
                global start, end
                start = self.file1.GetValue().split('/')[2] + self.file1.GetValue().split('/')[0] + self.file1.GetValue().split('/')[1]
                end = self.file2.GetValue().split('/')[2] + self.file2.GetValue().split('/')[0] + self.file2.GetValue().split('/')[1]
                fun2_2(event)
            else:
                self.text1.Destroy()
                self.text2.Destroy()
                self.file1.Destroy()
                self.file2.Destroy()
                self.searchButton.Destroy()
                self.text4 = wx.StaticText(self.panel, label='No Found', size=(200, 100))
                # panel
                self.panel.SetSizer(self.text4)


    # windowed
    window = window()
    # window show
    window.Show()
    # mainwindow
    mainWindow = window

# button2-2
def fun2_2(event):
    # main window
    global mainWindow, start, end
    # closewindow
    mainWindow.Close()
    # class window
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="第一个wxPython", size=(1200, 800))
            # initial
            self.sql = '''select BORO, 
                                  COUNT(CASE WHEN VIOLATION_CODE = '10F' THEN 1 END) non_food,
                                  COUNT(CASE WHEN VIOLATION_CODE = '08A' THEN 1 END) facility,
                                  COUNT(CASE WHEN VIOLATION_CODE = '02G' THEN 1 END) gold_food,
                                  COUNT(CASE WHEN VIOLATION_CODE = '04L' THEN 1 END) evidence_of_mice,
                                  COUNT(CASE WHEN VIOLATION_CODE = '06D' THEN 1 END) food_contact,
                                  COUNT(1)                                              num
                             from NYC_Restaurant_Inspections
                            where substr(INSPECTION_DATE,7,4) || substr(INSPECTION_DATE,1,2) || substr(INSPECTION_DATE,4,2) between '{}' and '{}'
                            GROUP BY BORO
                       '''.format(start, end)
            cur.execute(self.sql)
            self.data = cur.fetchall()
            # datanormalization
            x = list(map(lambda x: x[0], self.data))
            y1 = list(map(lambda x: x[1], self.data))
            y2 = list(map(lambda x: x[2], self.data))
            y3 = list(map(lambda x: x[3], self.data))
            y4 = list(map(lambda x: x[4], self.data))
            y5 = list(map(lambda x: x[5], self.data))
            # drafting
            self.get_img(x, y1, y2, y3, y4, y5)
            # pannel
            self.panel = wx.Panel(self)
            # component
            self.mainButton = wx.Button(self.panel, label='Violation Distribution', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30))
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30))
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            self.image = wx.StaticBitmap(self.panel, -1, wx.Bitmap("./p2.png", wx.BITMAP_TYPE_ANY))
            # layout size
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.VERTICAL)
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer1, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.sizer3, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            self.sizer5.Add(self.image, flag=wx.ALL, border=5)
            # layout sizer
            self.panel.SetSizer(self.sizer5)
            # button bind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, fun2)

        def get_img(self, x, y1, y2, y3, y4, y5):
            bar = Bar(init_opts=opts.InitOpts(
                        width="570px",
                        height="280px",
                        bg_color="white"
                    ))
            bar.add_xaxis(xaxis_data=x)
            # first parameter is the heading
            bar.add_yaxis(series_name='Non-food', y_axis=y1, stack='stack', z=0)
            bar.add_yaxis(series_name='Facility', y_axis=y2, stack='stack', z=0)
            bar.add_yaxis(series_name='Gold food', y_axis=y3, stack='stack', z=0)
            bar.add_yaxis(series_name='Evidence of mice', y_axis=y4, stack='stack', z=0)
            bar.add_yaxis(series_name='Food contact', y_axis=y5, stack='stack', z=0)
            bar.set_global_opts(yaxis_opts=opts.AxisOpts(type_="value", name="Count", position="left"),
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)))
            bar.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position='insider'))
            # image snapshot
            make_snapshot(snapshot, bar.render(), "p2.png")

    # windowed
    window = window()
    #window show
    window.Show()
    # main window
    mainWindow = window

# button3
def fun3(event):
    global mainWindow
    mainWindow.Close()
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initial data
            self.sql = "select * from NYC_Restaurant_Inspections limit 20"
            cur.execute(self.sql)
            self.data = cur.fetchall()
            # first page
            self.page = 0
            # index
            self.index = rows
            # panel
            self.panel = wx.Panel(self)
            # components
            self.mainButton = wx.Button(self.panel, label='Violation Keyword', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='Keyword', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text3 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30))
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30))
            self.file3 = wx.TextCtrl(self.panel, size=(150, 30))
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            self.grid = wx.grid.Grid(parent=self.panel)
            self.backButton = wx.Button(self.panel, label='<', size=(40, 20))
            self.nextButton = wx.Button(self.panel, label='>', size=(40, 20))
            # layout
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer4 = wx.BoxSizer(wx.VERTICAL)
            self.sizer5 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer6 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer7 = wx.BoxSizer(wx.VERTICAL)
            # layout get
            self.get_set(self.data)
            # button bind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, self.search)
            self.backButton.Bind(wx.EVT_BUTTON, lambda event, page=-1: self.get_page(event, page))
            self.nextButton.Bind(wx.EVT_BUTTON, lambda event, page=1: self.get_page(event, page))

        def get_set(self, data):
            # inherited table
            table = MyGridTable(data, self.index)
            self.grid.SetTable(table, True)
            self.grid.AutoSize()
            # layout
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.text3, flag=wx.ALL, border=5)
            self.sizer3.Add(self.file3, flag=wx.ALL, border=5)
            self.sizer4.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.sizer3, flag=wx.ALL, border=5)
            self.sizer5.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer1, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer6.Add(self.backButton, flag=wx.ALL, border=5)
            self.sizer6.Add(self.nextButton, flag=wx.ALL, border=5)
            self.sizer7.Add(self.sizer5, flag=wx.ALL, border=5)
            self.sizer7.Add(self.grid, flag=wx.ALL, border=5)
            self.sizer7.Add(self.sizer6, flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
            # panel
            self.panel.SetSizer(self.sizer7)

        def search(self, event):
            if len(self.file2.GetValue()) == 10 and len(self.file3.GetValue()) == 10 and len(self.file2.GetValue().replace('/', '')) == 8 and len(self.file3.GetValue().replace('/', '')) == 8:
                global start, end
                start = self.file2.GetValue().split('/')[2] + self.file2.GetValue().split('/')[0] + self.file2.GetValue().split('/')[1]
                end = self.file3.GetValue().split('/')[2] + self.file3.GetValue().split('/')[0] + self.file3.GetValue().split('/')[1]
                self.sql = "select * from NYC_Restaurant_Inspections where substr(INSPECTION_DATE,7,4) || substr(INSPECTION_DATE,1,2) || substr(INSPECTION_DATE,4,2) between '{}' and '{}' and VIOLATION_DESCRIPTION like '%{}%'".format(start, end, self.file1.GetValue())
                cur.execute(self.sql)
                self.data = cur.fetchall()
                # first page
                self.page = 0
                # set page
                self.get_set(self.data[self.page: self.page + 20])
            else:
                self.text1.Destroy()
                self.text2.Destroy()
                self.text3.Destroy()
                self.file1.Destroy()
                self.file2.Destroy()
                self.file3.Destroy()
                self.searchButton.Destroy()
                self.grid.Destroy()
                self.backButton.Destroy()
                self.nextButton.Destroy()
                self.text4 = wx.StaticText(self.panel, label='No Found', size=(200, 100))
                # panel set
                self.panel.SetSizer(self.text4)

        def get_page(self, event, page):
            if page == -1 and self.page == 0:
                pass
            elif page == 1 and int(self.index[-1]) >= len(self.data):
                pass
            else:
                # page update
                self.page += page
                # update index
                self.index = list(map(lambda x: str(int(x) + page * 20), self.index))
                # update label
                # self.text = wx.StaticText(self.panel, label=str(self.page), size=(10, 20))
                # get page
                self.get_set(self.data[self.page * 20: self.page * 20 + 20])

    # windowed
    window = window()
    # show
    window.Show()
    # mainwindow
    mainWindow = window

# button4
def fun4(event):
    # window
    global mainWindow
    # close window
    mainWindow.Close()
    # class window
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initial data
            self.sql = "select * from NYC_Restaurant_Inspections limit 20"
            cur.execute(self.sql)
            self.data = cur.fetchall()
            # panel
            self.panel = wx.Panel(self)
            # component
            self.mainButton = wx.Button(self.panel, label='Animal related case', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30))
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30))
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            # layout size
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.VERTICAL)
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer1, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.sizer3, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            # panel
            self.panel.SetSizer(self.sizer5)
            # buttonbind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, self.search)

        def search(self, event):
            if len(self.file1.GetValue()) == 10 and len(self.file2.GetValue()) == 10 and len(self.file1.GetValue().replace('/', '')) == 8 and len(self.file2.GetValue().replace('/', '')) == 8:
                global start, end
                start = self.file1.GetValue().split('/')[2] + self.file1.GetValue().split('/')[0] + self.file1.GetValue().split('/')[1]
                end = self.file2.GetValue().split('/')[2] + self.file2.GetValue().split('/')[0] + self.file2.GetValue().split('/')[1]
                fun4_2(event)
            else:
                self.text1.Destroy()
                self.text2.Destroy()
                self.file1.Destroy()
                self.file2.Destroy()
                self.searchButton.Destroy()
                self.text4 = wx.StaticText(self.panel, label='No Found', size=(200, 100))
                # panel
                self.panel.SetSizer(self.text4)


    # windowed
    window = window()
    # show window
    window.Show()
    # mainwindow
    mainWindow = window

# button4_2
def fun4_2(event):
    # window
    global mainWindow, start, end
    # mainwindow close
    mainWindow.Close()
    # class window
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initial data
            self.sql = '''select substr(INSPECTION_DATE,7,4), 
                                  COUNT(CASE WHEN BORO = 'BRONX' THEN 1 END),
                                  COUNT(CASE WHEN BORO = 'BROOKLYN' THEN 1 END),
                                  COUNT(CASE WHEN BORO = 'MANHATTAN' THEN 1 END),
                                  COUNT(CASE WHEN BORO = 'QUEENS' THEN 1 END),
                                  COUNT(CASE WHEN BORO = 'STATEN ISLAND' THEN 1 END)
                             from NYC_Restaurant_Inspections
                            where substr(INSPECTION_DATE,7,4) || substr(INSPECTION_DATE,1,2) || substr(INSPECTION_DATE,4,2) between '{}' and '{}'
                              and VIOLATION_DESCRIPTION = "Evidence of mice or live mice present in facility's food and/or non-food areas."
                            GROUP BY substr(INSPECTION_DATE,7,4)
                       '''.format(start, end)
            cur.execute(self.sql)
            self.data = cur.fetchall()
            # data normolization
            x = list(map(lambda x: x[0], self.data))
            y1 = list(map(lambda x: x[1], self.data))
            y2 = list(map(lambda x: x[2], self.data))
            y3 = list(map(lambda x: x[3], self.data))
            y4 = list(map(lambda x: x[4], self.data))
            y5 = list(map(lambda x: x[5], self.data))
            # drawing
            self.get_img(x, y1, y2, y3, y4, y5)
            # panel
            self.panel = wx.Panel(self)
            # component
            self.mainButton = wx.Button(self.panel, label='Violation Distribution', size=(150, 100))
            self.text1 = wx.StaticText(self.panel, label='StartDate', size=(60, 50))
            self.text2 = wx.StaticText(self.panel, label='EndDate', size=(60, 50))
            self.file1 = wx.TextCtrl(self.panel, size=(150, 30), )
            self.file2 = wx.TextCtrl(self.panel, size=(150, 30), )
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            self.image = wx.StaticBitmap(self.panel, -1, wx.Bitmap("./p4.png", wx.BITMAP_TYPE_ANY))
            # layout size
            self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer3 = wx.BoxSizer(wx.VERTICAL)
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.sizer1.Add(self.text1, flag=wx.ALL, border=5)
            self.sizer1.Add(self.file1, flag=wx.ALL, border=5)
            self.sizer2.Add(self.text2, flag=wx.ALL, border=5)
            self.sizer2.Add(self.file2, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer1, flag=wx.ALL, border=5)
            self.sizer3.Add(self.sizer2, flag=wx.ALL, border=5)
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.sizer3, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            self.sizer5.Add(self.image, flag=wx.ALL, border=5)
            # panel
            self.panel.SetSizer(self.sizer5)
            # bind button
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, fun4)

        def get_img(self, x, y1, y2, y3, y4, y5):
            line = Line(init_opts=opts.InitOpts(
                        width="570px",
                        height="280px",
                        bg_color="white"
                    ))
            line.add_xaxis(xaxis_data=x)
            # first parameter is heading
            line.add_yaxis(series_name='BRONX', y_axis=y1)
            line.add_yaxis(series_name='BROOKLYN', y_axis=y2)
            line.add_yaxis(series_name='MANHATTAN', y_axis=y3)
            line.add_yaxis(series_name='QUEENS', y_axis=y4)
            line.add_yaxis(series_name='STATEN ISLAND', y_axis=y5)
            line.set_global_opts(yaxis_opts=opts.AxisOpts(type_="value", name="Count", position="left"))
            # line.set_series_opts(label_opts=opts.LabelOpts(is_show=True, position='insider'))
            # snapshot
            make_snapshot(snapshot, line.render(), "p4.png")

    # windowed
    window = window()
    # show window
    window.Show()
    # main window
    mainWindow = window


# Button5
def fun5(event):
    # mainwindow
    global mainWindow
    # windowclose
    mainWindow.Close()
    # window frame
    class window(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, title="NYC", size=(1200, 800))
            # initialsql
            self.sql = "select * from NYC_Restaurant_Inspections limit 20"
            # panel
            self.panel = wx.Panel(self)
            # define component
            self.mainButton = wx.Button(self.panel, label='Borough', size=(150, 100))
            self.select = wx.ComboBox(self.panel, value='MANHATTAN', choices=['MANHATTAN', 'BRONX', 'BROOKLYN', 'QUEENS', 'STATEN ISLAND'], style=wx.CB_SORT)
            self.searchButton = wx.Button(self.panel, label='Find', size=(100, 50))
            self.grid = wx.grid.Grid(parent=self.panel)
            # layout size
            self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer5 = wx.BoxSizer(wx.VERTICAL)
            # layout
            self.get_set()
            # buttonbind
            self.mainButton.Bind(wx.EVT_BUTTON, main)
            self.searchButton.Bind(wx.EVT_BUTTON, self.search)

        def search(self, event):
            self.sql = "select * from NYC_Restaurant_Inspections where BORO = '{}' limit 100".format(self.select.GetValue())
            # layout
            self.get_set()

        def get_set(self):
            # tablesetting
            table = MyGridTable(self.sql)
            self.grid.SetTable(table, True)
            self.grid.AutoSize()
            # layout size
            self.sizer4.Add(self.mainButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.select, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer4.Add(self.searchButton, flag=wx.ALL | wx.CENTER, border=20)
            self.sizer5.Add(self.sizer4, flag=wx.ALL, border=5)
            self.sizer5.Add(self.grid, flag=wx.ALL, border=5)
            # layout
            self.panel.SetSizer(self.sizer5)

    # windowed
    window = window()
    # windowshow
    window.Show()
    # mainwindow
    mainWindow = window


def main(event):
    # mainwindow
    global mainWindow
    # closewindow or not
    if mainWindow == None:
        pass
    else:
        mainWindow.Close()
    # window frame
    window = wx.Frame(None, title="NYC", size=(1200, 800))
    # pannelset
    panel = wx.Panel(window)
    # layout VERTICAL/HORIZONTAL
    sizer = wx.BoxSizer(wx.VERTICAL)
    # define component
    button1 = wx.Button(panel, label='Time', size=(150, 100))
    button2 = wx.Button(panel, label='Violation Distribution', size=(150, 100))
    button3 = wx.Button(panel, label='Violation Keyword', size=(150, 100))
    button4 = wx.Button(panel, label='Button4', size=(150, 100))
    button5 = wx.Button(panel, label='Borough', size=(150, 100))
    # layoutadd
    sizer.Add(button1, proportion=0, flag=wx.ALL | wx.CENTER, border=20)
    sizer.Add(button2, proportion=0, flag=wx.ALL | wx.CENTER, border=20)
    sizer.Add(button3, proportion=0, flag=wx.ALL | wx.CENTER, border=20)
    sizer.Add(button4, proportion=0, flag=wx.ALL | wx.CENTER, border=20)
    sizer.Add(button5, proportion=0, flag=wx.ALL | wx.CENTER, border=20)
    # buttonbind
    button1.Bind(wx.EVT_BUTTON, fun1)
    button2.Bind(wx.EVT_BUTTON, fun2)
    button3.Bind(wx.EVT_BUTTON, fun3)

    button5.Bind(wx.EVT_BUTTON, fun5)
    # layout
    panel.SetSizer(sizer)
    # window
    window.Show()
    # mainwindow
    mainWindow = window

# table create
create_table(cur)
# insert table
insert_table(cur, con)
# startapp
app = wx.App()
mainWindow = None
main(None)
# main loop
app.MainLoop()