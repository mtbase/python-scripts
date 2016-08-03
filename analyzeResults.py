#!/usr/bin/env python

# analyzes a bunch of results given a certain directory by following the
# directory structure produced by runExperiments.py. Creates two files,
# summary.txt and summary.tex with the summarized results (once in CSV and once
# in Latex table format).
#
# Usage:
# First, configure anything between START CONFIG and END CONFIG, then run
# ./analyzeResults.py


import os
from os import walk
import sys

# START CONFIG
result_base_path            = "res1"    # result base path that was used in runExperiments
significant_digits          = 2         # number of signficant digits to round to
# END CONFIG

def writeToFiles (value, files):
    for f in files:
        f.write(value)

def analyzeFileSet (resultFiles, dirpath, fileNames):
    # query results : map from query term to (map of optimization levels to time)
    queryResults = {}
    optimization_levels = {}
    for fileName in (fileNames):
        inFile = open("{0}/{1}".format(dirpath, fileName), "r+")
        optimization_level = fileName.split("_")[0]
        optimization_levels[optimization_level] = ""
        currentQueryTerm = ""
        for line in inFile:
            if (line.startswith("-- Q")):
                currentQueryTerm = line.split(" ")[1].strip()
            elif (line.startswith("Time: ") and currentQueryTerm != ""):
                time = float(line.split(" ")[1])
                if not queryResults.has_key(currentQueryTerm):
                    queryResults[currentQueryTerm] = {}
                if not queryResults[currentQueryTerm].has_key(optimization_level):
                    queryResults[currentQueryTerm][optimization_level] = 0.0
                queryResults[currentQueryTerm][optimization_level] += time
        inFile.close()

    # latex table header
    resultFiles[1].write("\\begin{tabular}{|l")
    for i in range(len(queryResults)):
        resultFiles[1].write("|c")
    resultFiles[1].write("|}\n\t\\hline\n")

    # table head
    resultFiles[1].write("\t{\\bf Level}")
    resultFiles[0].write("Level")
    for queryTerm in sorted(queryResults):
        resultFiles[0].write("\t{0}".format(queryTerm))
        resultFiles[1].write(" & {{\\bf {0}}}".format(queryTerm))
    resultFiles[1].write(" \\\\\n\t\\hline\\hline")
    writeToFiles("\n", resultFiles)

    # table content
    for optimization_level in sorted(optimization_levels):
        resultFiles[1].write("\t")
        writeToFiles(optimization_level, resultFiles)
        for queryTerm in sorted(queryResults):
            resultFiles[0].write("\t")
            resultFiles[1].write(" & ")
            if queryResults[queryTerm].has_key(optimization_level):
                # round value to significant digits
                roundingString = '%.{0}g'.format(significant_digits)
                fi = '%s' % float (roundingString % queryResults[queryTerm][optimization_level])
                if fi.endswith(".0") and len(fi) > (significant_digits+1):
                    fi = fi.replace(".0", "")
                # write value
                writeToFiles(fi, resultFiles)
            else:
                writeToFiles("n/a", resultFiles)
        resultFiles[1].write(" \\\\\n\t\hline")
        writeToFiles("\n", resultFiles)

    # latex table footer
    resultFiles[1].write("\\end{tabular}")
    writeToFiles("\n", resultFiles)

def run():
    resultFileName = result_base_path + "/summary.txt"
    resultFiles = (
        open(resultFileName, "w+"),                         # plain txt file 
        open(resultFileName.replace(".txt", ".tex"), "w+")  # latex file
    )
    writeToFiles("All results are end-to-end response times in seconds", resultFiles)

    for (dirpath, dirnames, filenames) in walk(result_base_path):
        filteredFileNames = filter(lambda x : x.endswith("out.txt"), filenames)
        if len(filteredFileNames) > 0:
            splitted = dirpath.split("/")
            numSplits = len(splitted)
            engine = splitted[numSplits-3]
            dataParams = splitted[numSplits-2]
            scenario = splitted[numSplits-1]
            sf = int(dataParams.split("_")[2])
            writeToFiles("\n\nData Params: {0}, Engine: {1}, Scenario: {2}\n".format(
                    dataParams, engine, scenario)
                    .replace("_", "-"),
                    resultFiles)
            writeToFiles("----------------------\n", resultFiles)
            analyzeFileSet(resultFiles, dirpath, filteredFileNames)
    for f in resultFiles:
        f.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result_base_path = sys.argv[1]
    run()

