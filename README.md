# Introduction
This directory contains scripts for comparing different methods of overheatbath algorithms of CPN NLSM.
The two methods compared are the standard algorithm in the paper (original), and the modified algorithm with random phi (rand_phi).

# Files
- `func_CPNSampler.py`: Basic class for CPN NLSM sampling and some utility functions.
- `CPN_HB_compare.py`: Main script to perform the comparison between the two algorithms. Produces output files with measurements, saved in the `data` directory.
- `CPN_HB_compare_plot.ipynb`: Post-processing notebook to visualize and analyze the results from the comparison script.

# Usage
1. Run `CPN_HB_compare.py` to generate measurement data for both algorithms.
2. Run `CPN_HB_compare_plot.ipynb` to visualize the results and compare the performance of the two methods.

# Results
The results will be saved in the `figures` directory as plots comparing the performance of the original and modified algorithms in terms of runtime and various observables.
As for the observables, we measure the following (mean, error, and autocorrelation time):
- Energy density "E"
- Magnetic susceptibility "mag_sus"
- 1*1 Wilson loop calculated by $U(1)$ link variables "w_U"
- 1*1 Wilson loop calculated by $CP^{N-1}$ vertex variables "w_z"
- Topological susceptibility calculated by $U(1)$ link variables "top_sus_U"
- Topological susceptibility calculated by $CP^{N-1}$ vertex variables "top_sus_z"