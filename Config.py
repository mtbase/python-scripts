#!/usr/bin/env python

# Contains all the information that needs to be configured in order for the
# scripts to work properly

class DbConfig:
    dbType      = "postgres"        # postgres / mysql
    host        = "localhost"
    port        = 5432
    database    = "database"
    user        = "user"
    password    = "password"

# The tool chain is: inputfile ---(mt-rewrite)--> sqlfile ---(validate to explainFile / execute)--> resultFile
class RewriteConfig:
    execDir         = "mt-rewrite-exe"                  # location of MTRewrite executable
    optimizations   = ""                                # comma-separated values for optimizations to be used for rewriting,
                                                        # 't' (trivial optimizations), 'p' (client presentation push-up),
                                                        # 'c' (client conversion push-up), 'd' (conversion distribution)
    client          = "1"                               # Client parameter for MTSQL queries (input for rewriting)
    dataset         = "1,2,3,4,5,6,7,8,9,10"            # Dataset parameter for MTSQL queries (input for rewriting)
    inputFile       = "queries/postgres/orig.sql"       # MTSQL queries, one query per line (input for rewriting)
    sqlFile         = "queries/postgres/rewritten.sql"  # rewritten file (output of rewriting = input for validation/execution)
    explainFile     = "results/postgres/explain.txt"    # output file for query validation
    warnFile        = "results/postgres/warn.txt"       # file for output of warnings / errors during validation
    resultFile      = "results/postgres/result.txt"     # file for output of query results and execution times
    skip            = False     # If True, skips rewriting the queries from inputFile and assumes sqlFile already exists.
    explain         = False     # If True, validates the queries with EXPLAIN statements and stores the query plans in explainFile.
    execute         = False     # If True, executes the statements and stores the result (plus execution time) in resultFile.

# Only used in runExperiments.py
class BenchmarkConfig:
    benchmark_params= "zipf_s_1_t_10"                   # label that summarizes the data parameters that were used in the benchmark
                                                        # e.g. zipf distribution for tenants shares, scaling factor 1 and 10 tenants
                                                        # is used as directory name to store results in runExperiments.py

