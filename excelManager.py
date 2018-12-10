from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import datetime
from datetime import date

class ExcelManager(object):


    def __init__(self, targhet):
        self.dataA3 = date(2018, 12, 01)
        self.targhet = targhet
        self.file_name = targhet + '.xlsx'
        self.wb = self.load_excel(self.file_name)

    def load_excel(self, player):
        try:
            wb = load_workbook(player)
        except Exception as e:
            template = load_workbook('template.xlsx')
            template.save(player)
            template.close()
            wb = load_workbook(player)
        return wb

    def select_sheet(self, wb, coords, isMoon):
        sheet_name = coords;
        if isMoon:
            sheet_name = coords + ' (Luna)'

        try:
            ws = wb.get_sheet_by_name(sheet_name)
        except Exception as e:
            ws = wb.get_sheet_by_name("Empty")
            ws = wb.copy_worksheet(ws)
            ws.title = sheet_name
        return ws

    def findRow(self, ws):
        now = datetime.datetime.now ()
        time = str(now.hour) + str(now.minute) + '00'
        nOra = int(time)

        i = 3
        while i < 50:
            i = i + 1
            _min_t = int(str(ws['A' + str(i)].value).replace(':', ''))
            _max_t = int(str(ws['A' + str(i+1)].value).replace(':', ''))
            if (nOra > _min_t) and (nOra < _max_t):
                return i
        return i

    def findCol(self, ws):
        now = datetime.datetime.now()
        oggi = date(now.year, now.month, now.day)
        delta = oggi - self.dataA3
        return get_column_letter(delta.days + 2)

    def write_time(self, coords, isMoon, time):
        ws = self.select_sheet(self.wb, coords, isMoon)
        row = self.findRow(ws)
        col = self.findCol(ws)
        ws[col+str(row)] = time
        self.wb.save(self.file_name)


if __name__ == '__main__':
    excelManager = ExcelManager("Prova")
    excelManager.write_time("Ciao", True, 50)
