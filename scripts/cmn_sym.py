import colorama
from colorama import Fore, Back, Style

# mostly expect the entire line comes through line2
# occasionally line1 will get the segment name and the rest comes via line2
def parse_common_symbols(line1, line2, end, wb):
    if len(line2.split()) == 0:
        print(Fore.YELLOW +"parse_common_symbols: line 2 shall have at least 2 segments")
        return 0
    
    if len(line2.split()) == 2 and (line1 == None or len(line1.split()) == 0):
        print(Fore.YELLOW +"parse_common_symbols: if line 2 has 2 segments, then line1 shall have at least 1 segments")
        return 0

    # Excel output preparation
    sheetname = "CMN-SYM"
    active_rows = 0
    if sheetname not in wb.sheetnames:
        sheet = wb.create_sheet(sheetname)
        sheet['A1'] = "Note: This is a script generated sheet, any manual modifications will be lost!"
        sheet['A2'] = "S.No"
        sheet['B2'] = "Symbol Name"
        sheet['C2'] = "Size (bytes)"
        sheet['D2'] = "File Name"
        active_rows = 2
    else:
        sheet = wb[sheetname]
        active_rows = len(sheet['A'])

    # Handle the incoming line
    row = active_rows + 1
    sno = row - 2
    sheet['A'+str(row)] = sno
    if line1 == None:
        sheet['B'+str(row)] = line2.split()[0]
        sheet['C'+str(row)] = int(line2.split()[1], 16)
        sheet['D'+str(row)] = line2.split()[-1]
    else:
        sheet['B'+str(row)] = line1.split()[0]
        sheet['C'+str(row)] = int(line2.split()[0], 16)
        sheet['D'+str(row)] = line2.split()[-1]
    
    return 0

