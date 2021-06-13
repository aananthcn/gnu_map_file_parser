import colorama
from colorama import Fore, Back, Style

def parse_stack_memory_sections(line, end, wb):
    if len(line.split()) != 4:
        print(Fore.YELLOW +"parse_memory_configuration: line shall have at least 4 segments")
        if len(line.split()) >= 1:
            print(Fore.RESET + line)
        return 0
    
    # Excel output preparation
    sheetname = "STACK"
    active_rows = 0
    if sheetname not in wb.sheetnames:
        sheet = wb.create_sheet(sheetname)
        sheet['A1'] = "Note: This is a script generated sheet, any manual modifications will be lost!"
        sheet['A2'] = "S.No"
        sheet['B2'] = "Stack Segment"
        sheet['C2'] = "Size (hex)"
        sheet['D2'] = "Size (bytes)"
        active_rows = 2
    else:
        sheet = wb[sheetname]
        active_rows = len(sheet['A'])

    # Handle the incoming line
    row = active_rows + 1
    sno = row - 2
    sheet['A'+str(row)] = sno
    sheet['B'+str(row)] = line.split('=')[0].split()[-1]
    sheet['C'+str(row)] = line.split('=')[-1]
    sheet['D'+str(row)] = int(line.split('=')[-1], 16)
    
    return 0

