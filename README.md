# dk_nationwide_lidar
Software to generate high-resolution ecological descriptors of vegetation and terrain from Denmark’s national airborne laser scanning dataset. 

Code repository accompanying Assmann *et al.* 2021 - EcoDes-DK15: High-resolution ecological descriptors of vegetation and terrain derived from Denmark’s national airborne laser scanning dataset.

---

__*NOTE: This repository is currently under development.*__

## Variable Descriptions

A description of the output variables can be found [here](/documentation/variables.md) or download the [pdf](/documentation/variables.pdf).

## Repository Structure
```
/                 root folder
|- data/          empty, place-holder for the data (needs to be imported from external sources).
|- dklidar/       contains the Python modules providing the processing functions.
|- documentation/ variable descriptions and further documentation. 
|- log/           empty, place-holder for log file storage.
|- qa_local/      quallity assurance outputs and processing reports.
|- scratch/       empty, place-holder for temporary data handling.
|- scripts/       contains all batch, Python and R scripts for process management and QA.
```
## Getting Started

To get started with the processing check out the [workflow overview](/documentation/dk_lidar_processing_flow.pdf) and carry out the following steps:

1. Set up your local environment and download data following the instructions in  */scripts/readme.md* .
2. Basic processing for each tile is done with the */scripts/process_tile.py* script.
3. See */dklidar/readme.md* for an overview of the modules and functions of the *dklidar* Python package.

## Software

This project has been developed with OPALS 2.3.2.0, Python 2.7 (as distributed with OPALS), pandas (0.24.2), GDAL 2.2.4 (from OSgeo4W64) and SAGA GIS 7.8.2 executed on Windows 2012 Server 64 bit. 

## Contributors
PI leading the research for this project: Signe Normand (signe.normand@bio.au.dk)

Repository maintanance and code development: Jakob Assmann (j.assmann@bio.au.dk)

Selection and computation of output variables: Urs Treier, Andràs Zlinszky and Jesper Moeslund.

## Citation

When using the code or data please cite:

Assmann, Jakob J., Jesper E. Moeslund, Urs A. Treier and Signe Normand. *In prep*. EcoDes-DK15: High-resolution ecological descriptors of vegetation and terrain derived from Denmark’s national airborne laser scanning dataset.

## License
The code in this repository is freely available via a simplified BSD license. See [LICENSE.txt](license.txt) for the exact conditions. We highly encourage use and further development of the code provided.  

