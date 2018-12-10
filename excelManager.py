from openpyxl import load_workbook
import datetime

class ExcelManager(object):

    def __init__(self):
        pass

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
        print time

        i = 3
        while i < 50:
            i = i + 1
            _min_t = int(str(ws['A' + str(i)].value).replace(':', ''))
            _max_t = int(str(ws['A' + str(i+1)].value).replace(':', ''))
            if (nOra > _min_t) and (nOra < _max_t):
                return i
        return i


    def write_time(self, target, coords, isMoon, time):
        file_name = target + '.xlsx'
        wb = self.load_excel(file_name)
        ws = self.select_sheet(wb, coords, isMoon)

        row = self.findRow(ws)

        wb.save(file_name)
        wb.close()


if __name__ == '__main__':
    excelManager = ExcelManager()
    excelManager.write_time("Prova", "Ciao", True, 50)
