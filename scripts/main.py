import sys, os

import colorama
from colorama import Fore, Back, Style

import utils
import archives
import cmn_sym
import disca_sect
import memory
import stack_mem
import linker


def print_usage(prog):
    print("Usage:\n\t" + prog + " <map-file>")


def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        print("Trying to install " + package + " ...")
        pip.main(['install', package])


MapSegments = [
    "Archive member included to satisfy reference by file (symbol)",
    "Allocating common symbols",
    "Discarded input sections",
    "Memory Configuration",
    "Linker script and memory map",
    ".exec_boot_region",
    "LOAD ",
    ".debug_info"
]


def main(mapfile):
    map_content = []
    with open(mapfile) as file:
        map_content = file.readlines()

    # Open output excel sheet
    MapWb_name = os.path.dirname(mapfile)+"/MapExtract.xlsx"
    MapWb = utils.open_excel_out_file(MapWb_name)
    utils.clear_old_excel_rows(MapWb)

    parse_state = -1
    line1 = None
    sect_line = None

    # Parse the map file
    for line in map_content:

        # loop till the first segment string in MapSegments array is found
        if parse_state == -1:
            if MapSegments[0] in line:
                parse_state = 0
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
            continue

        # Parse archives and deps (note: 2 lines are needed to find out the dep module and function)
        if parse_state == 0:
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                continue
            if not '(' in line:
                continue
            if line1 == None:
                line1 = line
                continue
            if archives.parse_archives(line1, line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
            line1 = None
            continue

        # Parse Common Symbols
        if parse_state == 1:
            if "Common symbol" in line or len(line) == 0:
                continue
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                continue
            if len(line.split()) == 0:
                continue
            
            if line1 == None and len(line.split()) == 1:
                line1 = line
                continue
            
            if cmn_sym.parse_common_symbols(line1, line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
            line1 = None
            continue

        # Parse Discarded Input Sections
        if parse_state == 2:
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                continue
            if len(line.split()) == 0:
                continue
            
            if line1 == None and len(line.split()) == 1:
                line1 = line
                continue
            
            if disca_sect.parse_discarded_input_sections(line1, line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
            line1 = None
            continue
        
        # Parse Memory Sections
        if parse_state == 3:
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                continue
            if len(line.split()) == 0 or line.split()[1] == "Origin":
                continue

            if memory.parse_memory_configuration(line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
            continue


        # Parse Stack Memory Sections
        if parse_state == 4:
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                # GNU Map file does not have a clear separation between stack and other sections.
                # Hence using ".exec_boot_region" as both separator and new section name for new line.
                sect_line = line 
                continue
            if len(line.split()) == 0:
                continue

            if stack_mem.parse_stack_memory_sections(line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
                # GNU Map file does not have a clear separation between stack and other sections.
                # Hence using ".exec_boot_region" as both separator and new section name for new line.
                sect_line = line 
            continue


        # Parse Linker Sections
        if parse_state == 5:
            end = MapSegments[parse_state+1]
            if end in line:
                parse_state += 1
                print(Fore.LIGHTCYAN_EX +"Switching to state => " + MapSegments[parse_state])
                continue

            if sect_line != None:
                linker.parse_linker_sections(sect_line, line, end, MapWb)
                sect_line = None
                continue
            
            if line1 == None and len(line.split()) == 1:
                line1 = line
                continue
            

            if linker.parse_linker_sections(line1, line, end, MapWb):
                parse_state += 1
                print(Fore.CYAN +"Switching to state => " + MapSegments[parse_state])
            line1 = None
            continue

        # Todo: you are here!!


    # Clean up and save output Excel file
    if "Sheet" in MapWb.sheetnames:
        MapWb.remove(MapWb["Sheet"])
    try:
        MapWb.save(MapWb_name) # save contents before exit
    except:
        print("Error: File busy!")
    print(Fore.RESET +"End of main()")



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