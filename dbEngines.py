#!/usr/bin/env python

#################
# PREREQUISITS: #
#################
# - pymysql
# - pg8000
#################

import pymysql
import pg8000

from Config import DbConfig
from datetime import datetime

# IMPLEMENTATIION -- the actual class API is at the end of this file!

class _AbstractEngine:

    def __init__(self):
        self.host = DbConfig.host
        self.port = DbConfig.port
        self.database = DbConfig.database
        self.user = DbConfig.user
        self.password = DbConfig.password

    # returns the approximate execution time as a floating point number in seconds
    def getTime(self):
        return self.time

    def startTimer(self):
        self.started = datetime.now()

    def stopTimer(self):
        delta = datetime.now() - self.started
        self.time = delta.total_seconds()

    def execute(self, stmt):
        self.startTimer()
        self.cursor.execute(stmt)
        self.stopTimer()

    def getResult(self):
        return self.cursor.fetchmany(100)

    def close(self):
        self.cursor.close()
        self.connection.close()

    def rollback(self):
        self.connection.rollback()

class _PostgresEngine(_AbstractEngine):

    def __init__(self):
        _AbstractEngine.__init__(self)

    def connect(self):
        self.connection = pg8000.connect(
                host=self.host, port=self.port, database=self.database, user=self.user, password=self.password)
        self.connection.autocommit = False
        self.cursor = self.connection.cursor()
        self.cursor.execute("set max_parallel_degree = 64;")
        self.cursor.execute("set temp_tablespaces = temp_tbs;")
        self.cursor.execute("select pg_reload_conf();")

class _MySQLEngine(_AbstractEngine):

    def __init__(self):
        _AbstractEngine.__init__(self)

    def connect(self):
        # TODO: for now, mysql only works with default port, actually, you should be able to use "{0}:{1}" for the port
        # but it does not work right now...
        self.connection = pymysql.connect(
                host="{0}".format(self.host, self.port), database=self.database, user=self.user, password=self.password)
        self.connection.autocommit(False)
        self.cursor = self.connection.cursor()

## THIS is the ACTUAL interface to work with

class DbEngine:

    def __init__(self):
        if DbConfig.dbType == "postgres":
            self.instance = _PostgresEngine()
        elif DbConfig.dbType == "mysql":
            self.instance = _MySQLEngine()
        else:
            print "Unknown database type {0}".format(DbConfig.dbType)

    def connect(self):
        self.instance.connect()

    def execute(self, stmt):
        self.instance.execute(stmt)

    def getResult(self):
        return self.instance.getResult()

    # returns the approximate execution time in seconds
    def getTime(self):
        return self.instance.getTime()

    def close(self):
        return self.instance.close()

    def rollback(self):
        return self.instance.rollback()

