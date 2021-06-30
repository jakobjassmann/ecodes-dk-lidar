# Script to generate very basic EML metadata
# Jakob J. Assmann 23 June 2021

# Dependencies
library(EML)

# Title
title <- "EcoDes-DK15"

# Abstract
abstract <- set_TextType("documentation/eml_metadata/abstract.md")

# License
intellectualRights <- "This data is licensed under a Creative Commons Attribution 4.0 International License."

# Publication Date
pubDate <- "2021"

# Keywords
keywordSet <-
  list(
    list(
        keyword = list("ALS",
                       "LiDAR",
                       "Denmark",
                       "Biodiversity",
                       "Vegetation",
                       "Vegeation Structure",
                       "Terrain",
                       "Biodiversity")
        ))

# Authors
jakob <- as_emld(person(given = "Jakob J.", 
                        family = "Assmann", 
                        email = "j.assmann@bio.au.dk",
                        role = "cre",
                        comment = c(ORCID = "0000-0002-3492-8419")))

jesper <- as_emld(person(given = "Jesper R.", 
                        family = "Moeslund", 
                        role = "aut",
                        comment = c(ORCID = "0000-0001-8591-7149")))

urs <- as_emld(person(given = "Urs A.", 
                        family = "Treier", 
                        role = "aut",
                        comment = c(ORCID = "0000-0003-4027-739X")))

signe <- as_emld(person(given = "Signe", 
                        family = "Normand",  
                        role = "aut",
                        comment = c(ORCID = "0000-0002-8782-4154")))

associatedParty <- as_emld(c(jesper, urs, signe))

contact <- list(individualName = jakob$individualName,
                electronicMailAddress = jakob$electronicMailAddress)
# Coverage
geographicDescription <- "Denmark's terrestrial surface (incl. Bornholm)."
coverage <- 
  set_coverage(begin = '2014-04-03', end = '2015-11-24',
               geographicDescription = geographicDescription,
               west = 8.07, east = 15.20, 
               north = 54.56, south = 57.75,
               altitudeMin = 0, altitudeMaximum = 175,
               altitudeUnits = "meter")

# List raster variables
spatialRaster <- list(
  list(
    entityName = "canopy_height",
    entityDescription = "Altitude above ground of the 95th-percentile of all vegetation point returns.",
    physical = list(objectName ="canopy_height.vrt",
                    dataFormat = list(
                      externallyDefinedFormat = list(
                        formatName = "VRT/GeoTiff"
                      )
                    )
    ),
    attributeList = list(
      attribute = list(
        attributeName = "canopy_height",
        attributeDefinition = "Altitude above ground of the 95th-percentile of all vegetation point returns.",
        measurementScale = list(
          ratio = list(
            unit = list(
              standardUnit = "meter"
            ),
            numericDomain = list(
              numberType = "real"
            )
          )
        )
      )
    ),
    spatialReference = list(
      horizCoordSysName = "ETRF_1989_UTM_Zone_32N"),
    horizontalAccuracy = list(accuracyReport = "Empty"),
    verticallAccuracy = list(accuracyReport = "Empty"),
    cellSizeXDirection = 10,
    cellSizeYDirection = 10,
    numberOfBands = 1,
    rasterOrigin = "Lower Left", # Confirm!
    rows = 1, #Confirm
    columns = 1, # Confirm
    verticals = 1,
    cellGeometry = "pixel",
    scaleFactor = 1/100
  )
)



spatialRaster <- list(
  list(entityName = c(1,1),
       entityDescription = c(0,1),
       physical = c(0,"unbounded"),
       attributeList = c(1,1)
  )
)
spatialRaster <- 
  list(alternateIdentifier = list(0,"unbounded"),
       entityName = list(1,1),
       entityDescription = list(0,1),
       physical = list(0,"unbounded"),
       coverage = list(0,1),
       methods = list(0,1),
       additionalInfo = list(0,"unbounded"),
       annotation = list(0,"unbounded"),
       attributeList = list(1,1),
       constraint = list(0,"unbounded"),
       spatialReference = list(1,1),
       georeferenceInfo = list(0,1),
       horizontalAccuracy = list(1,1),
       verticalAccuracy = list(1,1),
       cellSizeXDirection = list(1,1),
       cellSizeYDirection = list(1,1),
       numberOfBands = list(1,1),
       rasterOrigin = list(1,1),
       rows = list(1,1),
       columns = list(1,1),
       verticals = list(1,1),
       cellGeometry = list(1,1),
       toneGradation = list(0,1),
       scaleFactor = list(0,1),
       offset = list(0,1),
       imageDescription = list(0,1),
       references = list(1,1)
  )

vrt_file <- emld::template("dataFormat")
vrt_file$externallyDefinedFormat <- list(formatName = "VRT")
spatialRasterTemplate <- emld::template("spatialRaster")
spatialRasterTemplate$alternateIdentifier <- ""
spatialRasterTemplate$entityName <- "canopy_height"
spatialRasterTemplate$entityDescription <- "canopy_height"
spatialRasterTemplate$physical <- list(objectName  ="canopy_height.vrt",
                                       size = 0,
                                       authentication = "",
                                       dataFormat = vrt_file)
spatialRasterTemplate$coverage <- coverage
spatialRasterTemplate$methods <- list()
spatialRasterTemplate$spatialReference <- "ETRF_1989_UTM_Zone_32N"
spatialRasterTemplate$cellSizeXDirection <- 10
spatialRasterTemplate$cellSizeYDirection <- 10
spatialRasterTemplate$coverage <- NULL

# Combine into dataset list
dataset <- list(
  title = title,
  creator = jakob,
  pubDate = pubDate,
  intellectualRights = intellectualRights,
  abstract = abstract,
  #associatedParty = associatedParty,
  keywordSet = keywordSet,
  coverage = coverage,
  contact = contact,
  spatialRaster = spatialRasterTemplate
)

# Create EML object
eml <- list(
  packageId = uuid::UUIDgenerate(),
  system = "uuid", # type of identifier
  dataset = dataset)
write_eml(eml, "documentation/eml_metadata/EcoDes-DK15.xml")

# Validate
eml_validate("documentation/eml_metadata/EcoDes-DK15.xml")
