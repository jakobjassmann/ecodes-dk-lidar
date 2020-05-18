# dk_nationwide_lidar
Raster outputs for ecological and environmental variables derived from DK nationwide LiDAR data "Punktsky".

---

__*NOTE: This repository is currently under development.*__

## General notes
This project has been developed with OPALS 2.3.2.0, Python 2.7 (as distributed with OPALS), pandas (0.24.2), SAGA GIS 2.3.2 (from OSGgeo4W64) and GDAL 2.2.4 (from OSgeo4W64) executed on Windows 2012 Server 64 bit. 

## Repository Structure
```
/                 root folder
|- data/          empty, place-holder for the data (needs to be imported from external sources).
|- dklidar/       contains the Python package with modules for processing.
|- log/           empty, place-holder for log file storage.
|- qa_local/      quallity assurance outputs and processing report.
|- scratch/       empty, place-holder for temporary data handling.
|- scripts/       contains all Batch and Python scritps for carrying out the processsing.
```
## Getting Started
1. Set up your local environment and download data following the instructions in  */scripts/readme.md* .
2. Basic processing for each tile is done with the */scripts/process_tile.py* script.
3. See */dklidar/readme.md* for an overview of the modules and functions of the *dklidar* Python package.

## Contributors
PI leading the research for this project: Signe Normand (signe.normand@bios.au.dk)

Repository maintanance and code development: Jakob Assmann (j.assmann@bios.au.dk)

Selection and computation of output variables: Urs Treier, Andràs Zlinszky and Jesper Moeslund.

## License
Content in this repository is currently not avialalbe under any license. Please contact Jakob (j.assmann@bios.au.dk) if you would like to re-use or share any of the code in this repostiory. 

