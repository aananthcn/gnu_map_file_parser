# gnu_map_file_parser

## Python3 installation
Install python3 on Windows or Linux

## Usage
To analyze map file and generate excel file:<br>
`python3 scripts/gnu-map-parser.py "gnu-map-file"`<br><br>
To create component breakup:<br>
`python3 scripts/component-breakup.py "input-excel"`

If everything is alright, it will generate an excel file in the path were the "gnu-map-file" is located. That excel should give a detailed break-up of different memory sections and memory usage.
