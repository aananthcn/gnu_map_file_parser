import colorama
from colorama import Fore, Back, Style

import utils

# mostly expect the entire line comes through line2
# occasionally line1 will get the segment name and the rest comes via line2
def parse_linker_sections(line1, line2, end, wb):
    if line1 != None and len(line2.split()) <= 1:
        print(Fore.YELLOW +"parse_linker_sections: if line1 != None, then line 2 shall have at least 2 segments")
        return 0
    if line1 == None and len(line2.split()) < 3:
        print(Fore.YELLOW +"parse_linker_sections: if line1 == None, then line 2 shall have at least 3 segments")
        print(Fore.LIGHTMAGENTA_EX +line2)
        return 0

    # Excel output preparation
    sheetname = "LinkerSections"
    active_rows = 0
    if sheetname not in wb.sheetnames:
        sheet = wb.create_sheet(sheetname)
        sheet['A1'] = "Note: This is a script generated sheet, any manual modifications will be lost!"
        sheet['A2'] = "S.No"
        sheet['B2'] = "Linker Section"
        sheet['C2'] = "Start Address"
        sheet['D2'] = "Size (hex)"
        sheet['E2'] = "Size (bytes)"
        sheet['F2'] = "Object File (optional)"
        sheet['G2'] = "Path (optional)"
        active_rows = 2
    else:
        sheet = wb[sheetname]
        active_rows = len(sheet['A'])

    # Handle the incoming line
    row = active_rows + 1
    sno = row - 2

    # capture all lines with 4 segments, but ignore then if starts with "0x"
    if len(line2.split()) >= 4 and line2.split()[0][0:2] != "0x" and utils.is_hex(line2.split()[2]):
        sheet['A'+str(row)] = sno
        sheet['B'+str(row)] = line2.split()[0] # discard line1
        sheet['C'+str(row)] = line2.split()[1]
        sheet['D'+str(row)] = line2.split()[2]
        sheet['E'+str(row)] = int(line2.split()[2], 16)
        sheet['F'+str(row)] = " ".join(line2.split()[3:]).split("/")[-1]
        sheet['G'+str(row)] = " ".join(line2.split()[3:])

    # capture all "fill" bytes
    if len(line2.split()) == 3 and "fill" in line2.split()[0] and utils.is_hex(line2.split()[2]):
        sheet['A'+str(row)] = sno
        sheet['B'+str(row)] = line2.split()[0]
        sheet['C'+str(row)] = line2.split()[1]
        sheet['D'+str(row)] = line2.split()[2]
        sheet['E'+str(row)] = int(line2.split()[2], 16)
        if len(line2.split()) > 3:
            sheet['F'+str(row)] = " ".join(line2.split()[3:]).split("/")[-1]
            sheet['G'+str(row)] = " ".join(line2.split()[3:])
    
    # capture segments that are printed across 2 lines
    if line1 != None and line2.split()[0][0:2] == "0x":
        if utils.is_hex(line2.split()[1]):
            sheet['A'+str(row)] = sno
            sheet['B'+str(row)] = line1.split()[0]
            sheet['C'+str(row)] = line2.split()[0]
            sheet['D'+str(row)] = line2.split()[1]
            sheet['E'+str(row)] = int(line2.split()[1], 16)
            if len(line2.split()) > 2:
                sheet['F'+str(row)] = " ".join(line2.split()[2:]).split("/")[-1]
                sheet['G'+str(row)] = " ".join(line2.split()[2:])
        else:
            print(Fore.RED + line2)

    # capture all 3 segment lines with valid data (e.g. ".bss")
    if len(line2.split()) == 3 and utils.is_hex(line2.split()[1]) and utils.is_hex(line2.split()[2]):
        sheet['A'+str(row)] = sno
        sheet['B'+str(row)] = line2.split()[0]
        sheet['C'+str(row)] = line2.split()[1]
        sheet['D'+str(row)] = line2.split()[2]
        sheet['E'+str(row)] = int(line2.split()[2], 16)

    return 0

