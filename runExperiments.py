#!/usr/bin/env python

# runs the MT-rewrite process and query execution for a couple of different
# (C/D-) scenarios, database engines, and for a numer of different optimization
# levels (see rewriteExecuteQueryFile.py or mt-rewrite for more information
# about optimization levels).
# Runs are repeated as many times as there exist entries in result_base_paths.
#
# Usage:
# First, configure anything between START CONFIG and END CONFIG plus
#   BenchmarkConfig in Config.py, then run
# ./runExperiments.py

import os

from rewriteExecuteQueryFile import run
from Config import DbConfig, RewriteConfig, BenchmarkConfig

## START CONFIG ##
def configureDB():
    if DbConfig.dbType == "mysql":
        DbConfig.host        = "localhost"
        DbConfig.port        = 3306
        DbConfig.database    = "mtbase"
        DbConfig.user        = "user"
        DbConfig.password    = "password"
    elif DbConfig.dbType == "postgres":
        DbConfig.host        = "localhost"
        DbConfig.port        = 5432
        DbConfig.database    = "mtbase"
        DbConfig.user        = "user"
        DbConfig.password    = "password"
    else:
        print "No configuration for engine {0}!".format(DbConfig.dbType)

def runExperiments():
    query_path                  = "queries"         # path to location where query files are stored
    result_base_paths           = ["res1", "res2"]  #
    db_engines                  = {             # engines for which to generate rewritten queries (with boolean for rewrite/validate/execute)
        "mysql"     : (False, False, False),    # for all of these engines, configureDB() has to be defined properly
        "postgres"  : (False, False, False)
    }
    scenarios                   = {             # map from scenario-name to scenarios, given as (C,D) pairs, an empty D means all
        "c_1_d_1_to_10" :   ("1", "1,2,3,4,5,6,7,8,9,10"),
        "c_1_d_1"       :   ("1", "1"),
        "c_2_d_1"       :   ("2", "1"),
        "c_1_d_2"       :   ("1", "2"),
        "c_1_d_all"     :   ("1", "")
    }
    optimization_levels         = {             # map from optimization-level-name to a set of optimization passes
        "canonical" : "",
        "o1"        : "t",
        "o2"        : "t p c",
        "o3"        : "t p c d",
        "o4"        : "t p c d i",
        "inl-only"  : "t i"
    }

## END CONFIG ##

    for db_engine in db_engines:
        DbConfig.dbType = db_engine
        configureDB()
        RewriteConfig.skip = not db_engines[db_engine][0]
        RewriteConfig.explain = db_engines[db_engine][1]
        RewriteConfig.execute = db_engines[db_engine][2]
        RewriteConfig.inputFile = "{0}/{1}/orig.sql".format(query_path, db_engine)
        for scenario in scenarios:
            RewriteConfig.client = scenarios[scenario][0]
            scenario_path = "{0}/{1}/rewritten/{2}".format(query_path, db_engine, scenario)
            if not os.path.isdir(scenario_path):
                os.makedirs(scenario_path)
            for optimization_level in optimization_levels:
                # run the experiment n times and store the results in n different result base paths
                for result_base_path in result_base_paths:
                    resultPath = "{0}/{1}/{2}/{3}".format(result_base_path,
                            db_engine, BenchmarkConfig.benchmark_params,
                            scenario)
                    if db_engines[db_engine] and not os.path.isdir(resultPath):
                        os.makedirs(resultPath)
                    RewriteConfig.sqlFile = "{0}/{1}.sql".format(scenario_path, optimization_level)
                    RewriteConfig.explainFile = "{0}/{1}_explain.txt".format(resultPath, optimization_level)
                    RewriteConfig.warnFile = "{0}/{1}_warnings.txt".format(scenario_path, optimization_level)
                    RewriteConfig.resultFile = "{0}/{1}_out.txt".format(resultPath, optimization_level)
                    RewriteConfig.dataset = scenarios[scenario][1]
                    RewriteConfig.optimizations = optimization_levels[optimization_level]
                    run()

if __name__ == "__main__":
    runExperiments()

