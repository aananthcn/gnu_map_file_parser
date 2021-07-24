# This program generates an output excel sheet with break of RAM and Flash 
# memory based on the input excel sheet. The input excel sheet shall contain
# the following SHEETs as per the criteria given below:
#
# Component SHEET
# ---------------
# 1) A sheet named "Components" with title "Component" containing arch / 
#    logical names.
# 2) The same sheet "Components" shall contain another column named "Modules"
#    with file names.
#
# Linker Data SHEET
# -----------------
# 1) The name of the sheet shall be "LinkerSections".
# 2) The content shall be the output of gnu-map-parser.py (with fillowing 
#    columns: "Linker Section", "Size (bytes)", "Object Files")
#
# Section Dictionary
# ------------------
# 1) The name of the sheet shall be "SectionDict"
# 2) The sheet shall contain a column named "RAM" as title and section name 
#    with or without wild card "*" below it.
# 3) The sheet shall also contain another column named "Flash" as title and 
#    section names with or without wild card "*" below it.

import os
import sys

import utils



MandatorySheets = ["Components", "LinkerSections", "SectionDict"]
RAM_Sections = []
FlashSections = []
CompBreakUp = {}


def validate_input(wb, xl_file):
    sheetnames = wb.sheetnames
    for sheet in MandatorySheets:
        if sheet in sheetnames:
            continue
        else:
            print("Error: sheet \""+sheet+"\" not found in "+ xl_file)
            print("       Can't compute breakup!")
            return -1
    return 0



def parse_linker_section(wb, sheetname):
    print("Info: Parsing linker sections with size info from input excel sheet")
    lsec = []
    lcol, row = utils.locate_heading_column("Linker Section", wb, sheetname)
    scol, row = utils.locate_heading_column("Size (bytes)", wb, sheetname)
    fcol, row = utils.locate_heading_column("Object File", wb, sheetname)

    sheet = wb[sheetname]
    rows = len(sheet[chr(lcol)])
    for i in range(row+1, rows+1):
        item = {}
        item["section"] = sheet[chr(lcol)+str(i)].value
        item["size"] = int(sheet[chr(scol)+str(i)].value)
        item["file"] = sheet[chr(fcol)+str(i)].value
        lsec.append(item)

    return lsec



def parse_components(wb, sheetname):
    print("Info: Parsing component list from input excel sheet")
    components = []
    ccol, row = utils.locate_heading_column("Component", wb, sheetname)
    mcol, row = utils.locate_heading_column("Module", wb, sheetname)
    scol, row = utils.locate_heading_column("Section", wb, sheetname)

    sheet = wb[sheetname]
    rows = len(sheet[chr(ccol)])
    for i in range(row+1, rows+1):
        item = {}
        # read component name
        item["component"] = sheet[chr(ccol)+str(i)].value
        # read all file names separated by comma or new line(s)
        modules = sheet[chr(mcol)+str(i)].value
        if modules != None:
            modules = modules.replace(' ', '').replace("\n", ',').replace(",,", ',')
            modules = modules.split(',')
        item["modules"] = modules
        # read special linker sections (like heap mem) assigned
        sections = sheet[chr(scol)+str(i)].value
        if sections != None:
            sections = sections.replace(' ', '').replace('\n', ',').replace(",,", ".")
            sections = sections.split(',')
        item["section"] = sections
        components.append(item)
    return components



def populate_ram_flash_sections(wb, sheetname):
    print("Info: Extracting RAM and Flash data from input data")
    rcol, row = utils.locate_heading_column("RAM", wb, sheetname)
    fcol, row = utils.locate_heading_column("Flash", wb, sheetname)

    sheet = wb[sheetname]
    rrows = len(sheet[chr(rcol)])
    frows = len(sheet[chr(fcol)])
    rows = max(rrows, frows)
    for i in range(row+1, rows):
        ram = sheet[chr(rcol)+str(i)].value
        if ram != None:
            RAM_Sections.append(ram)
        flash = sheet[chr(fcol)+str(i)].value
        if flash != None:
            FlashSections.append(flash)



def get_ram_flash_from_ls(obj, ls, ls_list):
    ram = 0
    flash = 0
    if obj != None:
        for item in ls_list:
            if obj == item["file"]:
                if item["section"] == None:
                    print("Error: input section without section name in", item["file"])
                    continue
                # all set, let us search item["section"] in RAM and Flash
                found = False
                # check if this is in RAM
                for rs in RAM_Sections:
                    if item["section"].startswith(rs):
                        found = True
                        ram += item["size"]
                        break
                # if found in RAM section, avoid searching in Flash
                if found:
                    continue

                # check if this is in flash
                for fs in FlashSections:
                    if item["section"].startswith(fs):
                        found = True
                        flash += item["size"]
                        break
                # raise error if still not found
                if not found:
                    print("Warning:", item["section", "is not part of RAM or Flash!"])
    if ls != None:
        for item in ls_list:
            if item["section"].startswith(ls):
                # all set, let us search item["section"] in RAM and Flash
                found = False
                # check if this is in RAM
                for rs in RAM_Sections:
                    if item["section"].startswith(rs):
                        found = True
                        ram += item["size"]
                        break
                # if found in RAM section, avoid searching in Flash
                if found:
                    continue

                # check if this is in flash
                for fs in FlashSections:
                    if item["section"].startswith(fs):
                        found = True
                        flash += item["size"]
                        break
                # raise error if still not found
                if not found:
                    print("Warning:", item["section"], "is not part of RAM or Flash! "+
                    str(item["size"]) + " bytes goes unaccounted!\n")
    return ram, flash



def add_data_to_comp_breakup(name, object, ram, flash):
    item_exist = False
    try:
        if CompBreakUp[name] != None:
            item_exist = True
    except KeyError:
        CompBreakUp[name] = {}
        CompBreakUp[name]["objects"] = []
        if object != None:
            CompBreakUp[name]["objects"].append(object)
        CompBreakUp[name]["ram"] = ram
        CompBreakUp[name]["flash"] = flash

    if item_exist:
        if object != None:
            CompBreakUp[name]["objects"].append(object)
        CompBreakUp[name]["ram"] += ram
        CompBreakUp[name]["flash"] += flash



def compute_comp_breakup(components, linker_sections):
    print("Info: Computing (adding) RAM and Flash data from extracted data")
    ignore = ["h", "E", "ld", "mk"]

    for cmp in components:
        add_data_to_comp_breakup(cmp["component"], None, 0, 0)
        if cmp["modules"] != None:
            for mod in cmp["modules"]:
                if mod != None and mod.split('.')[-1] in ignore:
                    continue
                mod = mod.split('.')[0]+".o"
                ram, flash = get_ram_flash_from_ls(mod, None, linker_sections)
                if ram != 0 or flash != 0:
                    add_data_to_comp_breakup(cmp["component"], mod, ram, flash)
        if cmp["section"] != None:
            for sec in cmp["section"]:
                ram, flash = get_ram_flash_from_ls(None, sec, linker_sections)
                if ram != 0 or flash != 0:
                    add_data_to_comp_breakup(cmp["component"], sec, ram, flash)



def clear_output_sheet(sheet, sheetname):
    header_size = 2 # First row will hold disclaimer, title in 2nd row
    active_rows = len(sheet['A'])
    if active_rows < header_size:
        print("Info: sheet \""+sheetname+"\" is new / fresh! So, not clearing old data!")
        return
    sheet.delete_rows(header_size+1, active_rows)


def add_comp_breakup_to_xl(wb):
    print("Info: Writing computed (RAM, Flash) data to Excel sheet")
    sheetnames = wb.sheetnames
    sheetname = "Output"
    if sheetname not in sheetnames:
        wb.create_sheet(sheetname)
        sheet = wb[sheetname]
        sheet['A1'] = "The data in this sheet are computer generated, any changes will be overwritten!"
        sheet['A2'] = "S.No"
        sheet['B2'] = "Component"
        sheet['C2'] = "Objects"
        sheet['D2'] = "RAM (bytes)"
        sheet['E2'] = "Flash (bytes)"
    else:
        clear_output_sheet(wb[sheetname], sheetname)

    sheet = wb[sheetname]
    i = 0
    for key in CompBreakUp:
        i += 1
        row = i + 2
        sheet['A'+str(row)] = i
        sheet['B'+str(row)] = key
        sheet['C'+str(row)] = ", ".join(CompBreakUp[key]["objects"])
        sheet['D'+str(row)] = CompBreakUp[key]["ram"]
        sheet['E'+str(row)] = CompBreakUp[key]["flash"]

def main(xl_file):
    xlwb = utils.open_excel_file(xl_file)
    if 0 != validate_input(xlwb, xl_file):
        return -1
    
    components = parse_components(xlwb, MandatorySheets[0])
    link_sects = parse_linker_section(xlwb, MandatorySheets[1])
    populate_ram_flash_sections(xlwb, MandatorySheets[2])

    compute_comp_breakup(components, link_sects)
    add_comp_breakup_to_xl(xlwb)

    print("Info: Saving Excel sheet and exiting!")
    try:
        xlwb.save(xl_file) # save contents before exit
    except:
        print("Error: File busy! Maybe it is opened already! Can't save "+ xl_file)
    xlwb.close()



def print_usage(prog):
    print("Usage:\n\t" + prog + " <cmp-breakup-excel-sheet>")
    print("\nFor more details, please read comments in top of file \"component-breakup.py\"\n")



if __name__ == '__main__':
    cmd_args = len(sys.argv)
    if cmd_args < 2:
        print_usage(sys.argv[0])
        exit(-1)
    
    # check and import pre-requisites
    utils.import_or_install("openpyxl")
    utils.import_or_install("colorama")

    if os.path.isfile(sys.argv[1]):
        main(sys.argv[1])
    else:
        print(sys.argv[1] + " is not a file! ERROR!")
