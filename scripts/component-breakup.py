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
        print("\t", obj, " RAM:", ram, " Flash:", flash)
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
                    print("Warning:", item["section", "is not part of RAM or Flash!"])
        print("\t", "["+ls+"]", " RAM:", ram, " Flash:", flash)
    return ram, flash



def compute_comp_breakup(components, linker_sections):
    item = {}
    cmp_brkup = []
    ignore = ["h", "E", "ld", "mk"]

    for cmp in components:
        print(cmp["component"]+"#")
        if cmp["modules"] != None:
            for mod in cmp["modules"]:
                if mod != None and mod.split('.')[-1] in ignore:
                    continue
                mod = mod.split('.')[0]+".o"
                ram, flash = get_ram_flash_from_ls(mod, None, linker_sections)
        if cmp["section"] != None:
            for sec in cmp["section"]:
                ram, flash = get_ram_flash_from_ls(None, sec, linker_sections)



def main(xl_file):
    xlwb = utils.open_excel_out_file(xl_file)
    if 0 != validate_input(xlwb, xl_file):
        return -1
    
    components = parse_components(xlwb, MandatorySheets[0])
    link_sects = parse_linker_section(xlwb, MandatorySheets[1])
    populate_ram_flash_sections(xlwb, MandatorySheets[2])
    cmp_brk_up = compute_comp_breakup(components, link_sects)

    #print(cmp_brk_up)



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
