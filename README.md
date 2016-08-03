# python-scripts
A handful of python scripts to execute MT-H on MTBase. These scripts are part
of the [MTBase project](https://github.com/mtbase/overview).

## Prerequisits
In order to run the scripts, you have to make sure that
    * you have installed [PyMySQL](https://github.com/PyMySQL/PyMySQL) and
      [PG8000](https://github.com/mfenniak/pg8000).
    * you have installed [MT-Rewite](https://github.com/lucasbraun/mt-rewrite).
    * you have populated your database with the [SQL
      scripts](https://github.com/mtbase/sql-scripts)
    * you have configured Config.py

## Using the scripts
Once this is done, you can use the following scripts, which are pretty much
self-explanatory if you look at the comments:
    * `rewriteExecuteQueryFile.py`: uses MT-Rewrite to rewrite, validate,
      and/or execute a file containing SQL queries for given MTSQL parameters C
      and D.
    * `runExperiments.py`: runs `rewriteExecuteQueryFile.py` several times with
      different C,D parameters, different optimization levels and different db
      engines.
    * `analyzeResults.py`: collects results obtained by `runExperiments.py` and
      summarizes them once in CSV and once in Latex table format.
