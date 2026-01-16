"""
Custom SQLite database backend that disables foreign key constraints
"""
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper

class DatabaseWrapper(SQLiteDatabaseWrapper):
    def _start_transaction_under_autocommit(self):
        self.cursor().execute("PRAGMA foreign_keys = OFF")
        super()._start_transaction_under_autocommit()
    
    def _set_autocommit(self, autocommit):
        super()._set_autocommit(autocommit)
        if autocommit:
            self.cursor().execute("PRAGMA foreign_keys = OFF")
