# EcoDes-DK Software and Documentation
Jakob J. Assmann, Jesper E. Moselund, Urs A. Treier and Signe Normand

Code repository accompanying the **EcoDes-DK15** dataset [INSERT BADGE](https://doi.org/10.5281/zenodo.4756557) and *Assmann* et al. in prep. - *EcoDes-DK15:* *High-resolution ecological descriptors of vegetation and terrain derived from Denmark’s national airborne laser scanning dataset.* [LINK TO DOI]().

## Content

1. [Getting Started](#getting-started)
2. [Repository Structure](#repository-structure)
3. [Documentation](#documentation)
4. [Software Requirements](#software-requirements)
5. [Contact](#contact)
6. [Acknowledgements](#Acknowledgements)
7. [Citation](#citation)
8. [License](#license)

## Getting Started

This repository contains the code needed to generate the EcoDes-DK15 dataset and the figures in accompanying manscuript, it also provides additional documentation for the dataset and the processing software.

We recommend the manuscript as a first starting point for information on both the dataset as well as the overall processing method. Further documentation for code and dataset, as well as example scripts on how to access the data are provided as outlined [below](#documentation). 

To get started with replicating the processing, please revisit the [workflow overview](/documentation/dk_lidar_processing_flow.pdf). Then carry out the following steps:

1. Set up your local environment and download the source data following the pre-processing steps in [*scripts/readme.md*](scripts/readme.md).
2. Process the tiles using [*scripts/process_tiles.py*](scripts/process_tiles.py).
3. Carry out the post-processing steps in [*scripts/readme.md*](scripts/readme.md).

[\[to top\]](#content)

## Repository Structure
```
/                 root folder.
|- data/          empty, place-holder for input (imported) and output (generated) data.
|- dklidar/       Python module providing the processing functions.
|- documentation/ documentation for python module and output variables. 
|- log/           empty, place-holder for log file output.
|- manuscript/ 		scripts and additional information accomapnying the manuscript.
|- qa_local/      quallity assurance outputs and processing reports.
|- scratch/       empty, place-holder for temporary data storage.
|- scripts/       contains Python and R scripts for process management and QA.
```
[\[to top\]](#content)

## Documentation

A description of the output variables can be found [here](/documentation/variables.md) or download the [pdf](/documentation/variables.pdf).

[\[to top\]](#content)

## Software Requirements

The processing workdflow was developed with OPALS 2.3.2.0, Python 2.7 (as distributed with OPALS), pandas (0.24.2), GDAL 2.2.4 and SAGA GIS 7.8.2. Newer versions of these software packages will likely work, but have not been tested. 

Code development and processing were carried out on Windows 2012 Server 64 bit, but execution should (in theory) be platform independent. 

[\[to top\]](#content)

## Contact
Repository maintanance and code development: Jakob Assmann (j.assmann@bio.au.dk)

PI leading the research for this project: Signe Normand (signe.normand@bio.au.dk)

[\[to top\]](#content)

## Acknowledgements

**TO BE COMPLETED**

From the manuscript:

*We would like to thank Andràs Zlinszky for his contributions to earlier versions of the dataset and Charles Davison for feedback regarding data use and handling. We would also like to thank the Section for EcoInformatics at Aarhus University for providing the computing resources required to process this dataset. Funding for this work was provided by the Carlsberg Foundation (XXXX to SN), AUFF Starting Grant (XXXX to SN).*

[\[to top\]](#content)

## Citation

When using the code contained in this repository please cite:

Assmann, Jakob J., Jesper E. Moeslund, Urs A. Treier and Signe Normand. *in prep*. EcoDes-DK15: High-resolution ecological descriptors of vegetation and terrain derived from Denmark’s national airborne laser scanning dataset.

[\[to top\]](#content)

## License

The code in this repository is openly available via a simplified BSD license. See [LICENSE.txt](license.txt) for details. We highly encourage use and further development of the code provided.  

[\[to top\]](#content)

