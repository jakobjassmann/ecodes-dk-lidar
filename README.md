# EcoDes-DK Software and Documentation
Jakob J. Assmann, Jesper E. Moselund, Urs A. Treier and Signe Normand

Code repository accompanying:

- The **EcoDes-DK15** v1.1.0 dataset [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4756557.svg)](https://doi.org/10.5281/zenodo.4756557)   
- Assmann, J. J., Moeslund, J. E., Treier, U. A., and Normand, S.: EcoDes-DK15: High-resolution ecological descriptors of vegetation and terrain derived from Denmark's national airborne laser scanning data set, Earth Syst. Sci. Data Discuss. [preprint], [https://doi.org/10.5194/essd-2021-222](https://doi.org/10.5194/essd-2021-222), in review, 2021. 

## Update: EcoDes-DK15 v1.1.0 (4 Dec. 2021)

Following the recommendations and feedback during the first round of peer-review, we updated the EcoDes-DK processing pipeline and EcoDes-DK15 data set. The key changes are:

- New version of the source data set optmised to contain only point data collected before the end of 2015. The source data for EcoDes-DK15 v1.0.0 unintentionally contained data from 2018. The new source data is documented in [/documentation/source_data/readme.md](/documentation/source_data/readme.md).
- New "date_stamp_*" auxiallary variables that illustrate the survey dates for the vegeation points in each cell. See updated descriptor documentation [/documentation/descriptors.md](/documentation/descriptors.md).
- Re-scaling of "solar_radiation" variable to MJ per 100 m2 per year. 
- Addtional support and quality control scripts. 

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

This repository contains the code for generating the EcoDes-DK15 dataset and the accompanying figures in the manscuript. The repository also provides additional documentation for the code and dataset, for details see [documentation](#documentation) below. 

> For thoughts and suggestions on how to transfer the workflow to another point cloud dataset (i.e. not the Danish DHM/Pointcloud), please read the [code_transfer](documentation/code_transfer.md) document.

To replicate the processing, revisit the [workflow overview](/documentation/dk_lidar_processing_flow.pdf), then carry out the following steps:

1. Obtain a local clone of this repository. 
2. Set up your local environment and download the source data following the pre-processing steps in [*scripts/readme.md*](scripts/readme.md).
3. Process the tiles using [*scripts/process_tiles.py*](scripts/process_tiles.py).
4. Carry out the post-processing steps in [*scripts/readme.md*](scripts/readme.md).

[\[to top\]](#content)

## Repository Structure
```
/                     root folder.
|- auxillary_files/   shapefiles needed for generating the sea and water masks. 
|- data/              empty, place-holder for input (imported) and output (generated) data.
|- dklidar/           Python modules providing the processing functions.
|- documentation/     documentation for Python modules and output descriptors. 
|- log/               empty, place-holder for log file output.
|- manuscript/        scripts accompanying the manuscript.
|- qa_local/          quallity assurance outputs and processing reports.
|- scratch/           empty, place-holder for temporary data storage.
|- scripts/           contains Python and R scripts for process management and QA.
```
[\[to top\]](#content)

## Documentation

This repository contains the following documentation:

- A summary of the output descriptors. See [/documentation/descriptors.md](/documentation/descriptors.md) (or as [pdf](/documentation/descriptors.pdf)).
- A lookup table for easy access to the descriptor conversion factors [/documentation/conversion_factors.csv](/documentation/conversion_factors.csv).
- A description of the source data set(s) can be found here: [/documentation/source_data/readme.md](/documentation/source_data/readme.md).
- Documentation for the pre- / post- processing and processing steps and scripts. See [/scripts/readme.md](/scripts/readme.md).
- Documentation for the *dklidar* Python processing modules. See [/documentation/dklidar_modules.md](/documentation/dklidar_modules.md).
- Example scripts for subsetting and working with the dataset. See [/manuscript/figure_7/subset_dataset.R](/manuscript/figure_7/subset_dataset.R) (subsetting) and [/manuscript/figure_7/figure_7.R](/manuscript/figure_7/figure_7.R) (ecological stratification).
- An example subset "teaser" (5 MB) of EcoDes-DK15 covering the 9 km x 9 km area of the Husby Klit plantation shown in the manuscript Figure 6 can be found here: [/manuscript/figure_7/EcoDes-DK15_teaser.zip](/manuscript/figure_7/EcoDes-DK15_teaser.zip)
- Scripts and data required to regenerate all figures in the manuscript:  [/manuscript/figure_X/](/manuscript/) 

[\[to top\]](#content)

## Software Requirements

The processing workflow was developed with OPALS 2.3.2.0, Python 2.7 (as distributed with OPALS), pandas (0.24.2), GDAL 2.2.4 and SAGA GIS 7.8.2. Newer versions of these software packages will likely work, but have not been tested. During peer-review we updated the processing pipeline for compatibility with GDAL 3.3.3. 

The R example scripts require R and the raster package. 

Code development and processing were carried out on Windows 2012 Server 64 bit, but execution should (in theory) be platform independent. 

[\[to top\]](#content)

## Contact
Code development and maintenance: Jakob J. Assmann (j.assmann@bio.au.dk)

PI overseeing this project: Signe Normand (signe.normand@bio.au.dk)

[\[to top\]](#content)

## Acknowledgements

From the manuscript:

*We would like to thank Andràs Zlinszky for his contributions to earlier versions of the dataset and Charles Davison for feedback regarding data use and handling. Funding for this work was provided by the Carlsberg Foundation (Distinguished Associate Professor Fellowships) and Aarhus University Research Foundation (AUFF-E-2015-FLS-8-73) to Signe Normand (SN). This work is a contribution to SustainScapes – Center for Sustainable Landscapes under Global Change (grant NNF20OC0059595 to SN).*

[\[to top\]](#content)

## Citation

When using the code contained in this repository please cite:

Assmann, Jakob J., Jesper E. Moeslund, Urs A. Treier and Signe Normand. *in prep*. EcoDes-DK15: High-resolution ecological descriptors of vegetation and terrain derived from Denmark’s national airborne laser scanning dataset.

[\[to top\]](#content)

## License

The code in this repository is openly available via a simplified BSD license. See [LICENSE](/LICENSE.txt) for details. We highly encourage use and further development of the code provided.  

[\[to top\]](#content)

