import colorama
from colorama import Fore, Back, Style

def parse_archives(line1, line2, end, wb):
    if end in line1 or end in line2:
        return 1

    if len(line1) == 0 or len(line2) == 0:
        print(Fore.YELLOW +"parse_archives: received empty lines")
        return 0

    # Excel output preparation
    sheetname = "Archives"
    active_rows = 0
    if sheetname not in wb.sheetnames:
        sheet = wb.create_sheet(sheetname)
        sheet['A1'] = "Note: This is a script generated sheet, any manual modifications will be lost!"
        sheet['A2'] = "S.No"
        sheet['B2'] = "Archive File"
        sheet['C2'] = "Dep Module"
        sheet['D2'] = "Object File"
        sheet['E2'] = "Function"
        active_rows = 2
    else:
        sheet = wb[sheetname]
        active_rows = len(sheet['A'])

    # Handle the incoming line
    row = active_rows + 1
    sno = row - 2
    sheet['A'+str(row)] = sno
    if '\\' in line1.split('(')[0]:
        sheet['B'+str(row)] = line1.split('(')[0].split('\\')[-1]
    else:
        sheet['B'+str(row)] = line1.split('(')[0].split('/')[-1]
    sheet['C'+str(row)] = line1.split('(')[-1].split(')')[0]
    if '\\' in line2.split('(')[0]:
        sheet['D'+str(row)] = line2.split('(')[0].split('\\')[-1]
    else:
        sheet['D'+str(row)] = line2.split('(')[0].split('/')[-1]
    sheet['E'+str(row)] = line2.split('(')[-1].split(')')[0]
    
    return 0

