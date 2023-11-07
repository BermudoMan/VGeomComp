from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Adding all *.dat file names to "file_in_the_RDF_directory" list

paths = sorted(Path('.\\RDF').glob('*.dat'))
file_in_the_RDF_directory = list(map(str, paths))

columns = 2
rows = len(file_in_the_RDF_directory) // columns + 1

plt.figure(figsize=(columns * 6, rows * 6))
for i, ax in enumerate(file_in_the_RDF_directory):
    data = np.loadtxt(file_in_the_RDF_directory[i])
    if len(file_in_the_RDF_directory) % 2 != 0:
        ax = plt.subplot(rows+1, columns, i + 1)
        r = data[:, 0]
        exp_fr = data[:, 1]
        th_fr = data[:, 2]
        delta_fr = data[:, 3] - 1.5
        ax.plot(r, exp_fr, color='red', linewidth=1, label='exp_fr')
        ax.plot(r, th_fr, color='green', linewidth=1, label='th_fr')
        ax.plot(r, delta_fr, label='delta_fr')
        ax.set_xlabel('r')
        ax.set_title(file_in_the_RDF_directory[i])
        ax.legend()
    else:
        ax = plt.subplot(rows, columns, i + 1)
        r = data[:, 0]
        exp_fr = data[:, 1]
        th_fr = data[:, 2]
        delta_fr = data[:, 3] - 1.5
        ax.plot(r, exp_fr, color='red', linewidth=1, label='exp_fr')
        ax.plot(r, th_fr, color='green', linewidth=1, label='th_fr')
        ax.plot(r, delta_fr, label='delta_fr')
        ax.set_xlabel('r')
        ax.set_title(file_in_the_RDF_directory[i])
        ax.legend()
plt.subplots_adjust(hspace=0.4)
plt.savefig('RDFcomp.png')



