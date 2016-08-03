#!/usr/bin/env python

# Takes a file with sql queries (each line is either a comment starting with
# '--' or a query) as input, performs the rewrite using the haskel-exe and
# RewriteConfig and writes the resulting queries into an output file.
# Additionally, (if RewriteConfig.explain is true) validates the query and (if
# RewriteConfig.execute is true) executes it and measures execution time. If
# RewriteConfig.skip is set, the query is not rewritten and the script assumes
# the rewritten query already being present. Check RewriteConfig in Config.py
# for details about the parameters that can be used in that script.
#
# Usage: ./rewriteExecuteQueryFiles (with optional parameters that can change
#       Config at run time)
# run ./rewriteExecuteQueryFiles -h to find out more about these parameters.

import sys

from argparse import ArgumentParser
from subprocess import Popen, PIPE

from Config import DbConfig, RewriteConfig
from dbEngines import DbEngine

def rewriteFile():
    print "Writing rewritten queries into [{0}]...".format(RewriteConfig.sqlFile)
    rewriteProcess = Popen(RewriteConfig.execDir, bufsize=4096, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (out, err) = rewriteProcess.communicate("l\n{0}\n{1}\n{2}\n{3}\nfile {4} {5}\n".format(
        RewriteConfig.client,
        RewriteConfig.dataset.replace(",", " "),
        DbConfig.dbType,
        RewriteConfig.optimizations.replace(",", " "),
        RewriteConfig.inputFile,
        RewriteConfig.sqlFile))
    print "[DONE]"

# if execute is True, really executes, otherwise only validates
def executeQueries(execQ=False):
    # save old stderr and redirect new one to file
    oldSysErr = sys.stderr
    warnFileString = RewriteConfig.warnFile
    if execQ:
        warnFileString = RewriteConfig.resultFile.replace(".txt", "_warn.txt")
    warnFile = open(warnFileString, "wb")
    sys.stderr = warnFile

    # open in and outFile
    inFile = open(RewriteConfig.sqlFile, 'r+')
    print "Readin from [{0}] ...".format(RewriteConfig.sqlFile)
    outFileString = RewriteConfig.explainFile
    if execQ:
        outFileString = RewriteConfig.resultFile
    outFile = open(outFileString, 'w+')
    print "Writing into [{0}] ...".format(outFileString)
    error = False

    # open database connection
    engine = DbEngine()
    engine.connect()
    currentComment = ""

    # validate (or execute) file line by line
    for line in inFile:
        if (line.startswith("-")):
            currentComment = line
            outFile.write(line)
        else:
            stmt = line
            if not execQ:
                if currentComment.__contains__("Q15"):
                    # Q15 statements cannot be checked with explain
                    outFile.write("No explanation possbile.\n")
                    continue
            try:
                if execQ:
                    print "{0}: executing {1}...".format((datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')), currentComment)
                engine.execute(stmt)
                if execQ:
                    outFile.write("Time: {0} secs\n".format(engine.getTime()))
                outFile.write("Result:\n======\n")
                if not line.lower().__contains__("view") and line != "GO;":
                    for row in engine.getResult():
                        outFile.write(str(row) + "\n")

            except Exception, e:
                engine.rollback()
                outFile.write("ERROR: " + str(e) + "\n")
                error = True
    engine.close()

    inFile.close()
    outFile.close()
    print "[DONE]"
  
    # restore old stderr and close warning file
    sys.stderr.flush()
    sys.stderr = oldSysErr
    warnFile.flush()
    warnFile.close()

    if error:
        print "There were some ERRORS. Please consult {0} and {1} for details.".format(warnFileString, outFileString)
    else:
        print "SUCCESS!"

def run():
    if not RewriteConfig.skip:
        print "REWRITING..."
        rewriteFile()
    if RewriteConfig.explain:
        print "EXPLAINING..."
        executeQueries(False)
    if RewriteConfig.execute:
        print "EXECUTING"
        executeQueries(True)

if __name__ == "__main__":
    # parse console arguments
    parser = ArgumentParser()
    optimizationHelperString = "comma-separate list of optimizations ('t'=trivial, 'p'=client presentation push-up, 'c'=client conversion push-up, 'd'=conversion distribution)"
    parser.add_argument("-e", dest='exec_dir', help="directory of the rewrite executable", default=RewriteConfig.execDir)
    parser.add_argument("-i", dest='input_file', help="input query file", default=RewriteConfig.inputFile)
    parser.add_argument("-o", dest='sql_file', help="sql file (output of rewrite, input to validate/execute)", default=RewriteConfig.sqlFile)
    parser.add_argument("-f", dest='explain_file', help="output query explain file", default=RewriteConfig.explainFile)
    parser.add_argument("-w", dest='warn_file', help="output file for warnings that arise during query validation", default=RewriteConfig.warnFile)
    parser.add_argument("-r", dest='result_file', help="output file for results and execution times", default=RewriteConfig.resultFile)
    parser.add_argument("-c", dest='client', help="ttid of the client that asks the queries", default=RewriteConfig.client)
    parser.add_argument("-d", dest='dataset', help="comma-separated list of ttids of tenants to query", default=RewriteConfig.dataset)
    parser.add_argument("-t", dest='db_type', help="db type / sql dialect (postgres/mysql)", default=DbConfig.dbType)
    parser.add_argument("-p", dest='optimizations', help=optimizationHelperString, default=RewriteConfig.optimizations)
    parser.add_argument("-x", dest='explain', help="create rewritten explain statements", default=RewriteConfig.explain, action="store_true")
    parser.add_argument("-q", dest='execute', help="executes the queries and measures executin time", default=RewriteConfig.execute, action="store_true")
    parser.add_argument("-k", dest='skip', help="skips query rewriting", default=RewriteConfig.skip, action="store_true")
    args = parser.parse_args()

    # setting parameters back into the config holder
    RewriteConfig.execDir       = args.exec_dir
    RewriteConfig.inputFile     = args.input_file
    RewriteConfig.sqlFile       = args.sql_file
    RewriteConfig.explainFile   = args.explain_file
    RewriteConfig.warnFile      = args.warn_file
    RewriteConfig.resultFile    = args.result_file
    RewriteConfig.client        = args.client
    RewriteConfig.dataset       = args.dataset
    DbConfig.dbType             = args.db_type
    RewriteConfig.optimizations = args.optimizations
    RewriteConfig.explain       = args.explain
    RewriteConfig.execute       = args.execute
    RewriteConfig.skip          = args.skip

    # do line-by-line rewriting validation, and execution if necessary
    run()

