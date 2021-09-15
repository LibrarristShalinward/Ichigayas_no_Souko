import re
from .html_chart import ChartView
from os import system as cmd
import _thread
from ..utils import id_name_trans


def space_trans(string):
    if type(string) == str:
        string = re.sub(" ", "&nbsp;" * 2, string)
    elif type(string) == list:
        for i in range(len(string)):
            string[i] = space_trans(string[i])
    elif type(string) == type(None):
        pass
    else:
        assert False, "仅可对字符串或字符串数组进行操作"
    return string

class HTMLPage():
    def __init__(self, rf = None, title = None, ant = None, chart = None) -> None:
        self.text = ["", "", "", ""]
        self.set_rfs(rf)
        self.set_title(title)
        self.set_ant(ant)
        self.set_chart(chart)
        self.__export_path = None

    def process_text(self, process_list = None):
        if type(process_list) == type(None):
            return process_list("rtac")
        if "r" in process_list:
            self.text[0] = "<meta http-equiv=\"refresh\" content=\"%f\">" %(1. / self.__refresh_frequency) if self.__refresh_frequency else ""
        if "t" in process_list:
            self.text[1] = "<h1>%s</h1>"%(self.__title) if self.__title else ""
        if "a" in process_list:
            self.text[2] = ""
            if self.__annotation:
                for ant in self.__annotation[:-1]:
                    self.text[2] += ant + "    "
                self.text[2] += self.__annotation[-1]
        if "c" in process_list:
            self.text[3] = ""
            if self.__chart:
                for line in self.__chart:
                    self.text[3] += line + "<br>"
    
    def export(self, path):
        self.set_export(path)
        export_text = self.text[0] + "<div><center>" + self.text[1] + self.text[2] + "</center></div><br><font size = \"3\"><div><center>" + self.text[3] + "</center></div></font>"
        export_text = space_trans(export_text)
        with open(self.__export_path, "w", encoding = "UTF-8") as f:
            f.writelines(export_text)
    
    def view(self):
        _thread.start_new_thread(cmd, (self.__export_path, ))

    def set_rfs(self, rf):
        self.__refresh_frequency = rf
        self.process_text("r")
    
    def set_title(self, title):
        self.__title = title
        self.process_text("t")
    
    def set_ant(self, ant):
        self.__annotation = ant
        self.process_text("a")
    
    def set_chart(self, chart):
        self.__chart = chart
        self.process_text("c")
    
    def set_export(self, path = None):
        self.__export_path = path if path else self.__export_path
        self.__export_path = self.__export_path if self.__export_path else self.__title + ".html"



class StaticHTMLChart(ChartView):
    def __init__(self, view: ChartView) -> None:
        self.copy(view)
        html = HTMLPage()
        html.set_title(id_name_trans(self.chart.get()[0]))
        html.set_ant((
            "序列号：%s"%(str(self.chart.get()[0]).zfill(3)), 
            "难度：%s"%(self.chart.get()[1]), 
            "速度：%i"%(int(self.chart.bpm)), 
            "时长：%is"%(int(self.line_time_stamp[-1])), 
            "物料量：%i"%(self.chart.amount), 
            "最大Combo：%i"%(self.chart.max_combo)))
        html.set_chart(self.get_line())
        self.__html = html
    
    def export(self, path = None):
        self.__html.export(path)
    
    def view(self):
        self.__html.view()