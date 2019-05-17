'''
Created on Apr 14, 2014

@author: pi

This file contains some testing code to access a sqlite database.
It should not be used.
Currently there are no plans to store the game data in sqlite.
'''
import sqlite3

DB_FILE_NAME = "./NonGit/srd35-db-SQLite-v1.3/dnd35.db"

class DatabaseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
class Database(object):
    '''
    This class provides a database access layer.
    '''

    @property
    def db(self):
        return self._db
    
    @property
    def cursor(self):
        return self._cursor

    def __init__(self):
        '''
        Constructor
        '''
        mydatabase=DB_FILE_NAME
        self._db = sqlite3.connect(mydatabase)
        #this makes returned rows behave like dictionaries
        self._db.row_factory = sqlite3.Row
        self._cursor = self.db.cursor()
    
    def getMonsterData(self,monsterId):
        '''
        Retrieve the monster data for the provided monsterId
        '''
        #Read set record from database
        QUERY = 'SELECT * ' + \
                'FROM monster ' + \
                'WHERE id = ' + str(monsterId)
        print(QUERY)
        self.cursor.execute(QUERY)
        rows = self.cursor.fetchall()
        print("Results:" + str(len(rows)))
        if len(rows) == 0:
            return None
        elif len(rows) == 1:
            return rows[0]
        else:
            raise DatabaseError("Multiple occurences of id " + str(monsterId) + " in monster table.")