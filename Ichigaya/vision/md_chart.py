from datetime import datetime as d


class MDLines:
    def __init__(self, path) -> None:
        self.set_path(path)
        self.__text = []
    
    def set_path(self, new_path):
        self.__path = new_path
    
    def write_line(self, line: str):
        self.__text.append(line)
    
    def delete_line(self):
        self.__text.pop(-1)
    
    def blank_line(self):
        self.write_line("")
        self.write_line("<br>")
        self.write_line("")
    
    def get_text(self):
        return self.__text
    
    def set_text(self, text: str):
        self.__text = text
    
    def clear_text(self):
        self.set_text = []
    
    def export(self, decoder = "UTF-8"):
        with open(self.__path, "w", encoding = decoder) as f:
            f.writelines(line + "\n" for line in self.__text)

class MDChart(MDLines):
    def __init__(self, path, title: str = "", col_title: list = [""]) -> None:
        super().__init__(path)
        self.set_title(title)
        self.set_col_title(col_title)
    
    def set_title(self, title: str = ""):
        self.__title = title
    
    def set_col_title(self, col_title: list = [""]):
        try:
            self.col_num = len(col_title)
            self.__list2line(col_title)
        except:
            assert False
        self.__col_title = col_title
    
    def __list2line(self, itemlist: list = []):
        assert len(itemlist) <= self.col_num, "列数异常，输入了%i列而目前表格有%i列" %(len(itemlist), self.col_num)
        while len(itemlist) < self.col_num:
            itemlist.append("")
        line = ""
        for item in itemlist:
            line += "|"
            try:
                line += str(item)
            except:
                pass
        line += "|"
        return line
    
    def write_line(self, line):
        if type(line) == str:
            return super().write_line(line)
        elif type(line) == list:
            return super().write_line(self.__list2line(line))
        else:
            assert False
    
    def write_table(self, table: list = [[]], title: str = "", col_title: list = [""], note: str = ""):
        past_text = self.get_text()
        self.clear_text()
        try: 
            self.set_title(title if title != "" else self.__title)
            self.set_col_title(col_title if col_title != [""] else self.__col_title)
        except:
            assert False
        self.write_line("<center>")
        self.write_line("")
        self.write_line("# " + self.__title)
        self.blank_line()
        self.write_line(note)
        self.write_line("更新于：" + d.strftime(d.now(), "%Y年%m月%d日"))
        self.write_line("")
        self.write_line("----")
        self.write_line("")
        self.write_line(self.__col_title)
        self.write_line([":--:"] * self.col_num)
        try:
            for line in table:
                self.write_line(line)
        except:
            self.set_text(past_text)
            assert False
    
    def export(self, decoder = "UTF-8"):
        if self.get_text() == []:
            self.write_table()
        return super().export(decoder=decoder)

