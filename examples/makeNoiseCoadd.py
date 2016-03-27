#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

from __future__ import with_statement
"""Make a coadd from gaussian noise images
"""
import os
import sys

import numpy

import lsst.afw.image as afwImage
import lsst.afw.image.testUtils as afwTestUtils
import lsst.coadd.chisquared as coaddChiSq
from noiseCoaddConfig import NoiseCoaddConfig

if __name__ == "__main__":
    #    pexLog.Trace.setVerbosity('lsst.coadd', 5)
    helpStr = """Usage: makeCoadd.py coaddPath numImages

where:
- coaddPath is the desired name or path of the output coadd
- numImages is the desired number of images

Make a chi-squared coadd from a set of Gaussian noise images.
The result should closely match the predicted chi squared distribution.
Run the resulting coadd through makeHistogram to see this.
"""
    if len(sys.argv) != 3:
        print helpStr
        sys.exit(0)

    coaddPath = sys.argv[1]
    weightPath = os.path.splitext(coaddPath)[0] + "_weight.fits"

    numImages = int(sys.argv[2])

    config = NoiseCoaddConfig()

    sys.stderr.write("""
coaddPath  = %s
numImages  = %d
imageShape = %s
imageSigma = %0.1f
variance   = %0.1f
""" % (coaddPath, numImages, config.imageShape, config.imageSigma, config.variance))

    numpy.random.seed(0)

    coadd = None
    for imInd in range(numImages):
        print >> sys.stderr, "Create exposure %d" % (imInd,)
        maskedImage = afwTestUtils.makeGaussianNoiseMaskedImage(
            dimensions=config.imageShape, sigma=config.imageSigma, variance=config.variance)
        # the WCS doesn't matter; the default will do
        wcs = afwImage.Wcs()
        exposure = afwImage.ExposureF(maskedImage, wcs)

        if not coadd:
            print >> sys.stderr, "Create coadd"
            coadd = coaddChiSq.Coadd.fromConfig(
                bbox = exposure.getBBox(),
                wcs = exposure.getWcs(),
                config = config.coadd)
            print >> sys.stderr, "badPixelMask=", coadd.getBadPixelMask()

        coadd.addExposure(exposure)

    print >> sys.stderr, "Save weight map as %s" % (weightPath,)
    weightMap = coadd.getWeightMap()
    weightMap.writeFits(weightPath)
    coaddExposure = coadd.getCoadd()
    print >> sys.stderr, "Save coadd as %s" % (coaddPath,)
    coaddExposure.writeFits(coaddPath)
