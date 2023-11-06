#! python3
import pathlib
from pathlib import Path
from itertools import islice
import subprocess
import time
import shutil, os

# import matplotlib

# Adding all *.log file names to "file_in_directory" list
paths = sorted(Path('.').glob('*.log'))
file_in_directory = list(map(str, paths))


# In each *.log file in directory find xyz coordinates and save them to the "COORDS" folder with .xyz extention

def xyz_cut_gaussian(marker_start, marker_end):
    way = str(Path.cwd()) + '\\XYZ'
    pathlib.Path(way).mkdir(parents=True, exist_ok=True)
    start_xyz = 0
    end_xyz = 0
    index = 0
    for i in file_in_directory:
        name = str(i).replace('.log', '') + '.xyz'
        writing_xyz = open(way + '\\' + name, '+w')
        reading_log = open(i, 'r')
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
    return print('.xyz copied to the XYZ folder')


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
    # ToDo avoid using time command!
    return print('.vm generated to the VM folder')


# For each *.log file in directory create .inp file in the "UNEX" folder on the basis of the template.inp file,
# for each .inp file run calculation in UNEX program
def unex_generation(start_vm, stop_vm):
    block_xyz = '<xyz>'
    block_ampl = '<ampl>'
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
        #                print(x)
        reading_vm.seek(0)
        for num_line, line in enumerate(reading_vm):
            if stop_vm in line:
                y = num_line - 1
        #                print(y)
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
        template.close()
        writing_unex_inp.close()
        reading_xyz.close()
        reading_vm.close()
        subprocess.Popen(['S:\\soft\\UNEX\\unex.exe', way + '\\' + name, way + '\\' + name.replace('.inp', '') + '.ks'])
    return print('.log generated in UNEX folder')


def ref_sms_found(points_number):
    way = str(Path.cwd()) + '\\UNEX\\'
    #    file_with_ref_sms = open(way + str(file_in_directory[0]).replace('.log', '_unex_1.log'), 'r')
    file_with_ref_sms = open(way + '2a_unex.ks', 'r')
    print('\n' + str(file_with_ref_sms))
    ref_sms = open(way + 'ref_sms.dat', '+w')
    start_sms_block = 'Set: 1-1'
    index = 0
    x = 0
    for line in iter(file_with_ref_sms):
        index += 1
        if start_sms_block in line:
            x = index + 13
    file_with_ref_sms.seek(0)
    for line_sms in islice(file_with_ref_sms, x - 1, x + points_number):
        ref_sms.write(line_sms[1:15] + line_sms[31:47] + '\n')
    file_with_ref_sms.close()
    ref_sms.close()
    # ToDo auto conformer seacrh corresponded min on the PES
    return print('ref_sms.dat generated')


# Paste ref_sms.dat to the <ref_sms>/<ref_sms> block of the template.inp
def paste_ref_sms(start_sms_block, end_sms_block):
    way = str(Path.cwd()) + '\\UNEX\\'
    template = open('template.inp', 'r')
    update_template = open('template_updated.inp', '+w')
    for line in iter(template):
        if start_sms_block not in line:
            update_template.write(line)
        else:
            break
    template.close()
    update_template.close()

    update_template = open('template_updated.inp', 'a')
    ref_sms = open(way + 'ref_sms.dat', 'r')
    update_template.write(start_sms_block + '\n')
    for sms_line in iter(ref_sms):
        update_template.write(sms_line)
    update_template.write(end_sms_block)
    update_template.close()
    ref_sms.close()

    shutil.copyfile('template_updated.inp', 'template.inp')
    os.remove('template_updated.inp')
    # ToDo think of a way to properly delete the unnecessary files


# Find in all .ks files block with "Radial distribution functions" data and save them to .dat file in the RDF directory
def RDF_search(RDF, points_number):
    way = str(Path.cwd()) + '\\RDF'
    pathlib.Path(way).mkdir(parents=True, exist_ok=True)
    index = 0
    x = 0
    for i in file_in_directory:
        reading_ks = open(str(Path.cwd()) + '\\UNEX\\' + str(i.replace('.log', '') + '_unex.ks'), 'r')
        writing_file = open(str(Path.cwd()) + '\\RDF\\' + str(i.replace('.log', '') + '.dat'), '+w')
        for line in iter(reading_ks):
            index += 1
            if RDF in line:
                x = index + 1
        reading_ks.seek(0)
        for RDF_lines in islice(reading_ks, x + 2, x + points_number + 1):
            writing_file.write(RDF_lines)
        x = 0
        index = 0
        writing_file.close()
        reading_ks.close()


xyz_cut_gaussian('Standard orientation', 'Basis read from chk')
# time.sleep(2)
vm_generation(298)
time.sleep(4)
unex_generation(' List of the data in the UNEX format', ' VibModule terminated normally.')
time.sleep(4)
ref_sms_found(269)
paste_ref_sms('<ref_sms> ', '</ref_sms> ')
unex_generation(' List of the data in the UNEX format', ' VibModule terminated normally.')
time.sleep(4)
RDF_search('Radial distribution functions:', 301)
