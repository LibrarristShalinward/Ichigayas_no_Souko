import re
from .html_chart import ChartView
from os import system as cmd
import _thread
from ..utils import id_name_trans
from time import time as t
from warnings import warn as w


def space_trans(string):
    if type(string) == str:
        string = re.sub(" ", "&nbsp;", string)
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
        self._export_path = None
        self.full_text = lambda: self.text[0] + "<div><center>" + space_trans(self.text[1]) + space_trans(self.text[2]) + "</center></div><font size=\"1.5\", face=\"Courier\"><div><center>" + space_trans(self.text[3]) + "</center></div></font>"

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
        export_text = self.full_text()
        with open(self._export_path, "w", encoding = "UTF-8") as f:
            f.writelines(export_text)
    
    def view(self):
        _thread.start_new_thread(cmd, (self._export_path, ))

    def set_rfs(self, rf):
        self.__refresh_frequency = rf
        self.process_text("r")
    
    def set_time(self, time):
        self.text[0] = "<meta http-equiv=\"refresh\" content=\"%f\">" %(time) if time else self.text[0]
    
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
        self._export_path = path if path else self._export_path
        self._export_path = self._export_path if self._export_path else self.__title + ".html"



class TimeKeeper():
    def __init__(self, stamps, decay = 1.) -> None:
        self.__time_stamps = stamps
        self.__start_decay = decay
        self.__i = 0
    
    def rein(self):
        st = t() + self.__start_decay
        self.table = [stm + st for stm in self.__time_stamps]
    
    def __call__(self):
        tar = self.table[self.__i]
        self.__i += 1
        while t() < tar:
            continue
        


class HTMLDynamic(HTMLPage):
    def __init__(self, rf, title, ant, charts, stamps) -> None:
        super().__init__(rf = rf, title = title, ant = ant, chart = None)
        self.set_charts(charts)
        self.set_stamps(stamps)
        self.pre_process()

    def set_charts(self, charts):
        self.__charts = charts
    
    def set_stamps(self, stamps):
        self.__stamps = stamps
        self.clock = TimeKeeper(self.__stamps)
    
    def pre_process(self):
        export_texts  = [self.full_text()]
        for i, chart in enumerate(self.__charts):
            self.set_time(self.__stamps[i + 1] - self.__stamps[i])
            self.set_chart(chart)
            export_texts.append(self.full_text())
        self.export_texts = export_texts
    
    def run(self, path):
        self.export(path)
        self.view()
        p = self._export_path
        clock = self.clock
        clock.rein()
        for text in self.export_texts:
            with open(p, "w", encoding = "UTF-8") as f:
                f.writelines(text)
            clock()
            
        

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
            "物料量：%i+%i+%i+%i"%(
                len(self.chart.keys["Single"]), 
                len(self.chart.keys["Flick"]), 
                len(self.chart.keys["Hold"]), 
                len(self.chart.keys["Direct"])), 
            "最大Combo：%i"%(self.chart.max_combo)))
        html.set_chart([str(i + 1).zfill(5) + line for i, line in enumerate(self.get_line())][::-1])
        self.__html = html
    
    def export(self, path = None):
        self.__html.export(path)
    
    def view(self):
        self.__html.view()



class DynamicHTMLChart(ChartView):
    def __init__(self, view: ChartView, lps = 2, rf = 60, sr = 64) -> None:
        self.copy(view)

        title = id_name_trans(self.chart.get()[0])
        annotation = (
            "序列号：%s"%(str(self.chart.get()[0]).zfill(3)), 
            "难度：%s"%(self.chart.get()[1]), 
            "速度：%i"%(int(self.chart.bpm)), 
            "时长：%is"%(int(self.line_time_stamp[-1])), 
            "物料量：%i+%i+%i+%i"%(
                len(self.chart.keys["Single"]), 
                len(self.chart.keys["Flick"]), 
                len(self.chart.keys["Hold"]), 
                len(self.chart.keys["Direct"])), 
            "最大Combo：%i"%(self.chart.max_combo))
        chart = [str(i + 1).zfill(5) + line for i, line in enumerate(self.get_line())]
        frgs = []
        stamps = [.5]
        for i in range((len(chart) - sr) // lps):
            frgs.append(chart[i * lps:i * lps + sr][::-1])
            try:
                stamps.append(self.line_time_stamp[i * lps + sr])
            except:
                stamps.append(stamps[-1] * 2 - stamps[-2])
        
        html = HTMLDynamic(rf, title, annotation, frgs, stamps)
        self.__html = html
    
    def run(self, path = None):
        self.__html.run(path)