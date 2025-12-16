# High-throughput Segregation Pyiron Workflow Demonstrator

High-throughput grain boundary segregation demonstrator using pyiron_workflow, pyiron_workflow_atomistics, and LAMMPS.

## Description

This repository contains Jupyter notebooks demonstrating high-throughput grain boundary segregation calculations using the pyiron_workflow framework.

### Notebooks

1. **`grain_boundary_segregation.ipynb`**: Complete workflow for calculating grain boundary segregation energies, including:
   - Crystal structure optimization
   - Solution energy calculations
   - Grain boundary structure generation and analysis
   - Segregation energy calculations for individual elements

2. **`publication_example_dataset.ipynb`**: Analysis and visualization of publication data
   - Analyzes the comprehensive dataset from our published study in [Acta Materialia (2025), DOI: 10.1016/j.actamat.2025.121288](https://doi.org/10.1016/j.actamat.2025.121288)
   - Reproduces all publication figures showing segregation and cohesion effects
   - Contains data for all periodic table elements at 6 CSL grain boundaries in Fe
   - Dataset generated using DFT (VASP) calculations with a workflow similar to `grain_boundary_segregation.ipynb`
   - Demonstrates analysis techniques for large-scale segregation datasets
   - Supplementary figures can be generated from the `SupplementaryFigures.ipynb` notebooks

## Requirements

- Python 3.12
- pyiron-workflow-atomistics
- pyiron-workflow-lammps
- LAMMPS (from conda-forge)

## Running on Binder

Click the badge below to launch the notebook in an interactive Binder environment:

[![Binder](https://notebooks.mpcdf.mpg.de/binder/badge_logo.svg)](https://notebooks.mpcdf.mpg.de/binder/v2/git/https%3A%2F%2Fgitlab.mpcdf.mpg.de%2Fhmai%2FHTSegregation_PyironWorkflow_Demonstrator.git/HEAD)
## Local Installation

### Using Conda (Recommended)

Create the environment from the `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate ht_segregation
```

### Using pip

Alternatively, install the required dependencies with pip:

```bash
pip install -e .
```

Or with notebook support:

```bash
pip install -e ".[notebook]"
```

## Usage

### Running the Workflow

Open and run the `grain_boundary_segregation.ipynb` notebook to execute the complete segregation workflow with LAMMPS calculations.

### Exploring Published Results

Open the `publication_example_dataset.ipynb` notebook to:
- Explore the comprehensive periodic table dataset
- Reproduce publication figures
- Analyze segregation trends across elements and GB types

## Citation

If you use this workflow or dataset in your research, please cite:

```bibtex
@article{FeGB_Segregation2025,
  title={A high-throughput ab initio study of elemental segregation and cohesion at ferritic-iron grain boundaries},
  journal={Acta Materialia},
  year={2025},
  author={Mai, Han Lin and Cui, Xiang-Yuan and Hickel, Tilmann and Neugebauer, Joerg and Ringer, Simon P},
  volume={297},
  pages={121288},
  doi={10.1016/j.actamat.2025.121288}
}
```

## Contact us
Open an issue or email: h(dot)mai(at)mpi-susmat(dot)de

## License

BSD License
