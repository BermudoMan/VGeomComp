#! python3
import pathlib
from pathlib import Path
from itertools import islice
import subprocess

# import matplotlib

# Adding all *.log file names to "file_in_directory" list
paths = sorted(Path('.').glob('*.log'))
file_in_directory = list(map(str, paths))


# In each *.log file in directory find xyz coordinates and save them to the "COORDS" folder with .xyz extention

def xyz_cut_gaussian():
    way = str(Path.cwd()) + '\\XYZ'
    pathlib.Path(way).mkdir(parents=True, exist_ok=True)
    start_xyz = 0
    end_xyz = 0
    index = 0
    for i in file_in_directory:
        name = str(i).replace('.log', '') + '.xyz'
        writing_xyz = open(way + '\\' + name, '+w')
        reading_log = open(i, 'r')
        marker_start = 'Standard orientation'
        marker_end = 'Basis read from chk'
        for line in iter(reading_log):
            index += 1
            if marker_start in line:
                start_xyz = index + 4
            if marker_end in line:
                end_xyz = index - 5
        reading_log.seek(0)
        for found_line in islice(reading_log, start_xyz, end_xyz):
            writing_xyz.write(found_line)
        index = 0
        start_xyz = 0
        end_xyz = 0
        reading_log.close()
        writing_xyz.close()


# For each *.log file in directory create .inp file in the "VM" folder, for each .inp file run calculation
# in VibModule program
def vm_generation(temperature):
    way = str(Path.cwd()) + '\\VM'
    pathlib.Path(way).mkdir(parents=True, exist_ok=True)
    for i in file_in_directory:
        name = str(i).replace('.log', '') + '.inp'
        writing_vm_inp = open(way + '\\' + name, '+w')
        writing_vm_inp.write('VIBMODULE' + '\n')
        writing_vm_inp.write('GAUSSIAN ' + i + '\n')
        writing_vm_inp.write('TEMP  ' + str(temperature) + '.' + '\n')
        writing_vm_inp.write('PRINTUNEX' + '\n')
        writing_vm_inp.write('STOP' + '\n')
        writing_vm_inp.close()
        subprocess.Popen(['S:\\soft\\VibModule\\vibmodule.exe', way + '\\' + name])
# ToDo figure out how to avoid specifying the full path to the vibmodule.exe file

# For each *.log file in directory create .inp file in the "UNEX" folder on the basis of the template.inp file,
# for each .inp file run calculation in UNEX program
def unex_inp_generation():
    block_xyz = '<xyz>'
    block_ampl = '<ampl>'
    start_vm = ' List of the data in the UNEX format'
    stop_vm = ' VibModule terminated normally.'
    x = 0
    y = 0
    way = str(Path.cwd()) + '\\UNEX'
    pathlib.Path(way).mkdir(parents=True, exist_ok=True)
    for i in file_in_directory:
        name = str(i.replace('.log', '')) + '_unex.inp'
        writing_unex_inp = open(way + '\\' + name, '+w')
        reading_xyz = open(str(Path.cwd()) + '\\XYZ\\' + str(i.replace('.log', '') + '.xyz'), 'r')
        reading_vm = open(str(Path.cwd()) + '\\VM\\' + str(i.replace('.log', '') + '.vm'), 'r')

        for num_line, line in enumerate(reading_vm):
            if start_vm in line:
                x = num_line + 2
                print(x)
        reading_vm.seek(0)
        for num_line, line in enumerate(reading_vm):
            if stop_vm in line:
                y = num_line - 1
                print(y)
        reading_vm.seek(0)

        template = open('template.inp', 'r')

        writing_unex_inp.write('BASE=BASE,<BASE>,</BASE>' + '\n')
        writing_unex_inp.write('MOLXYZ=mol,XYZGAUSSIAN,<xyz>,</xyz>' + '\n')
        writing_unex_inp.write('AMPLITUDES=mol,FREEU,<ampl>,</ampl>' + '\n')
        for inp_line in template:
            if block_xyz not in inp_line:
                writing_unex_inp.write(inp_line)
            elif block_xyz in inp_line:
                writing_unex_inp.write(block_xyz + '\n')
                for j in reading_xyz:
                    writing_unex_inp.write(j)
            if block_ampl in inp_line:
                writing_unex_inp.write('')
                for k in islice(reading_vm, x, y):
                    writing_unex_inp.write(k)
                x = 0
                y = 0


xyz_cut_gaussian()
vm_generation(298)
unex_inp_generation()
