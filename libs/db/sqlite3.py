import inspect
import re

from django.db.models import ForeignKey

from south.db import generic
from django.core.management.commands import inspectdb
    
class DatabaseOperations(generic.DatabaseOperations):

    """
    SQLite3 implementation of database operations.
    """
    
    backend_name = "sqlite3"

    # SQLite ignores several constraints. I wish I could.
    supports_foreign_keys = False
    has_check_constraints = False

    def add_column(self, table_name, name, field, *args, **kwds):
        """
        Adds a column.
        """
        # If it's not nullable, and has no default, raise an error (SQLite is picky)
        if (not field.null and 
            (not field.has_default() or field.get_default() is None) and
            not field.empty_strings_allowed):
            raise ValueError("You cannot add a null=False column without a default value.")
        # We add columns by remaking the table; even though SQLite supports 
        # adding columns, it doesn't support adding PRIMARY KEY or UNIQUE cols.
        self._remake_table(table_name, added={
            field.column: self._column_sql_for_create(table_name, name, field, False),
        })
    
    def _remake_table(self, table_name, added={}, renames={}, deleted=[], altered={}):
        """
        Given a table and three sets of changes (renames, deletes, alters),
        recreates it with the modified schema.
        """
        # Dry runs get skipped completely
        if self.dry_run:
            return
        # Temporary table's name
        temp_name = "_south_new_" + table_name
        # Work out the (possibly new) definitions of each column
        definitions = {}
        cursor = self._get_connection().cursor()
        # Get the index descriptions
        indexes = self._get_connection().introspection.get_indexes(cursor, table_name)
        # Work out new column defs.
        for column_info in self._get_connection().introspection.get_table_description(cursor, table_name):
            name = column_info[0]
            if name in deleted:
                continue
            # Get the type, ignoring PRIMARY KEY (we need to be consistent)
            type = column_info[1].replace("PRIMARY KEY", "")
            # Add on unique or primary key if needed.
            if indexes[name]['unique']:
                type += " UNIQUE"
            if indexes[name]['primary_key']:
                type += " PRIMARY KEY"
            # Deal with a rename
            if name in renames:
                name = renames[name]
            # Add to the defs
            definitions[name] = type
        # Add on altered columns
        definitions.update(altered)
        # Add on the new columns
        definitions.update(added)
        # Alright, Make the table
        self.execute("CREATE TABLE %s (%s)" % (
            self.quote_name(temp_name),
            ", ".join(["%s %s" % (self.quote_name(cname), ctype) for cname, ctype in definitions.items()]),
        ))
        # Copy over the data
        self._copy_data(table_name, temp_name, renames)
        # Delete the old table, move our new one over it
        self.delete_table(table_name)
        self.rename_table(temp_name, table_name)
    
    def _copy_data(self, src, dst, field_renames={}):
        "Used to copy data into a new table"
        # Make a list of all the fields to select
        cursor = self._get_connection().cursor()
        src_fields = [column_info[0] for column_info in self._get_connection().introspection.get_table_description(cursor, src)]
        dst_fields = [column_info[0] for column_info in self._get_connection().introspection.get_table_description(cursor, dst)]
        src_fields_new = []
        dst_fields_new = []
        for field in src_fields:
            if field in field_renames:
                dst_fields_new.append(self.quote_name(field_renames[field]))
            elif field in dst_fields:
                dst_fields_new.append(self.quote_name(field))
            else:
                continue
            src_fields_new.append(self.quote_name(field))
        # Copy over the data
        self.execute("INSERT INTO %s (%s) SELECT %s FROM %s;" % (
            self.quote_name(dst),
            ', '.join(dst_fields_new),
            ', '.join(src_fields_new),
            self.quote_name(src),
        ))
    
    def _column_sql_for_create(self, table_name, name, field, explicit_name=True):
        "Given a field and its name, returns the full type for the CREATE TABLE."
        field.set_attributes_from_name(name)
        if not explicit_name:
            name = field.db_column
        else:
            field.column = name
        sql = self.column_sql(table_name, name, field, with_name=False, field_prepared=True)
        #if field.primary_key:
        #    sql += " PRIMARY KEY"
        #if field.unique:
        #    sql += " UNIQUE"
        return sql
    
    def alter_column(self, table_name, name, field, explicit_name=True):
        """
        Changes a column's SQL definition
        """
        # Remake the table correctly
        self._remake_table(table_name, altered={
            name: self._column_sql_for_create(table_name, name, field, explicit_name),
        })

    def delete_column(self, table_name, column_name):
        """
        Deletes a column.
        """
        self._remake_table(table_name, deleted=[column_name])
    
    def rename_column(self, table_name, old, new):
        """
        Renames a column from one name to another.
        """
        self._remake_table(table_name, renames={old: new})
    
    # Nor unique creation
    def create_unique(self, table_name, columns):
        """
        Not supported under SQLite.
        """
        print "   ! WARNING: SQLite does not support adding unique constraints. Ignored."
    
    # Nor unique deletion
    def delete_unique(self, table_name, columns):
        """
        Not supported under SQLite.
        """
        print "   ! WARNING: SQLite does not support removing unique constraints. Ignored."

    # Not implemented this yet.
    def delete_primary_key(self, table_name):
        raise NotImplementedError()
    
    # No cascades on deletes
    def delete_table(self, table_name, cascade=True):
        generic.DatabaseOperations.delete_table(self, table_name, False)
