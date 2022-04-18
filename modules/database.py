import sys
import MySQLdb
import re
import json
from populate import datagen


class handle_db():
    """Class that handles database activities."""

    def __init__(self, **kwargs):
        """Initializes class."""
        ws = datagen.Warning_Singleton()
        try:
            self.host = kwargs.get('host')
            self.username = kwargs.get('username')
            self.password = kwargs.get('password')
            self.database = kwargs.get('database')
            self.db = None
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)

    def open_db(self):
        """Open database."""
        ws = datagen.Warning_Singleton()
        ws.wprint('Opening database...', 3)

        try:
            self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.database)
            ws.wprint('Database opened', 3)

            return self.db
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)

            return None

    def close_db(self):
        """Close database."""
        ws = datagen.Warning_Singleton()
        ws.wprint('Closing database...', 3)

        try:
            self.db.close()
            ws.wprint('Database closed', 3)

            return True
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)

            return None

    def get_tables(self):
        ws = datagen.Warning_Singleton()
        sql = 'SHOW TABLES;'
        records = self.runQuery(sql)
        if not records:
            return None
        records = [item[0] for item in records]
        return records


    def list(self, options):
        """List tables."""
        try:
            ws = datagen.Warning_Singleton()
            ws.wprint('Listing tables...', 3)
            records = self.get_tables()
            if not records:
                ws.wprint('No tables available', 1)
                return
            matrix = []
            if options['header'] and options['format'] == 'table':
                matrix = [['Table', 'Columns']]
            for table in records:
                sql = f'DESCRIBE {table};'
                items = self.runQuery(sql)
                if not items:
                    items = (('N/A',),)
                matrix.append([table] + [item[0] for item in items])
            if options['format'] == 'table':
                self.list_table(matrix, options)
            elif options['format'] == 'json':
                self.list_json(matrix, options)

        except (MySQLdb.OperationalError) as e:
            ws.sh_exc(sys.exc_info(), e)
            ws.wprint('Rolling back...', 3)
            db.rollback()
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)
        else:
            self.close_db()
        finally:
            ws.wprint('Listing finalized', 3)

    def list_table(self, matrix, options = {}):
        ws = datagen.Warning_Singleton()
        max_row = 0
        for row in matrix:
            max_row = len(row) if len(row) > max_row else max_row

        sizes = []
        for i in range(0, max_row):
            sizes.append(0)
        for row in matrix:
            for i, item in enumerate(row):
                if len(item) > sizes[i]:
                    sizes[i] = len(item)

        # print columns
        data = ''
        for row in matrix:
            fmt_string = ''
            for i, item in enumerate(row):
                fmt_string += '{' + str(i) + ':<' + str(sizes[i]) + '} '
            data += fmt_string.format(*row) + '\n'
        data = data[0:-1]
        self.list_printer(data, options)

    def list_json(self, matrix, options = {}):
        ws = datagen.Warning_Singleton()
        jsonMatrix = []
        for row in matrix:
            jsonMatrix.append({'table': row[0], 'columns': row[1:]})
        data = json.dumps(jsonMatrix)
        self.list_printer(data, options)

    def list_printer(self, data, options = {}):
        ws = datagen.Warning_Singleton()
        if options.get('output') == None:
            ws.wprint(data, 1)
        else:
            with open(options.get('output'), 'w') as f:
                f.write(data + '\n')

    def drop(self, options = {}):
        """List tables."""
        try:
            ws = datagen.Warning_Singleton()
            ws.wprint('Dropping tables...', 3)
            records = self.get_tables()
            records = [] if not records else records
            tables_to_drop = []
            if options['table'] == None:
                tables_to_drop = records
            else:
                tables_to_drop = options['table']
            if not options['respectForeignKeys']:
                sql = 'SET FOREIGN_KEY_CHECKS=0';
                self.runQuery(sql)
            for table in tables_to_drop:
                ws.wprint(f'Dropping table "{table}"...', 2)
                if table not in records:
                    ws.eprint(f'TABLE "{table}" not found')
                    continue
                yes = options['yesAll']
                result = None
                if not yes:
                    result = input(f'Do you confirm the dropping of TABLE "{table}" (y/N)? ')
                    result = True if result.upper() == 'Y' or result.upper() == 'YES' else False
                else:
                    result = True
                if result:
                    sql = 'DROP TABLE `' + table + '`;'
                    result = self.runQuery(sql)
                    if result:
                        ws.wprint(f'TABLE {table} successfuly dropped', 2)
                    else:
                        sql = f"SELECT table_type FROM information_schema.tables WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}';"
                        result = self.runQuery(sql, {'fetchone': True})
                        if result:
                            result = result[0]
                        if result != 'VIEW':
                            ws.eprint(f'Failed to drop TABLE {table}')
                            continue
                        else:
                            result = None
                            if not yes:
                                result = input(f'"{table}" is a \'VIEW\'. Delete the \'VIEW\' anyway (y/N)? ')
                                result = True if result.upper() == 'Y' or result.upper() == 'YES' else False
                            else:
                                result = True
                            if result:
                                sql = f'DROP VIEW `{table}`;'
                                result = self.runQuery(sql)
                                if result:
                                    ws.wprint(f'VIEW {table} successfuly dropped', 2)
                                else:
                                    ws.eprint(f'Failed to drop VIEW {table}')
                    # except BaseException as e:
                        # ws.sh_exc(sys.exc_info(), e)

        except (MySQLdb.OperationalError) as e:
            ws = datagen.Warning_Singleton()
            ws.sh_exc(sys.exc_info(), e)
            ws.wprint('Rolling back...', 3)
            db.rollback()
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)
        else:
            pass
        finally:
            ws.wprint('Dropping finalized', 3)
            if options['respectForeignKeys']:
                sql = 'SET FOREIGN_KEY_CHECKS=1';
                self.runQuery(sql)
            self.close_db()

    def runQuery(self, sql, options={}):
        ws = datagen.Warning_Singleton()
        if self.db is None:
            self.open_db()
        if self.db is None:
            raise MySQLdb._exceptions.DatabaseError('Error accessing database.')
            return None
        db = self.db
        cursor = db.cursor()
        try:
            result = cursor.execute(sql)
            records = True
            if (re.match('SELECT |SHOW |DESCRIBE |DESC ', sql, flags=re.IGNORECASE)):
                if (options.get('fetchone')):
                    records = cursor.fetchone()
                else:
                    records = cursor.fetchall()
            return records
        except (MySQLdb.OperationalError) as e:
            ws.sh_exc(sys.exc_info(), e)
            ws.wprint('Rolling back...', 3)
            db.rollback()
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)
        return None


class Datatype():
    """Class for defining basic datatypes."""

    def __init__(self, datatype='varchar', size=255, type_options=None, null='NULL'):
        """Initializes Data_Char_Base."""
        self.datatype = datatype
        self.size = size

        if type_options is None:
            self.type_options = ['default']
        else:
            self.type_options = type_options
        self.null = null


class Data():
    """Class holding database logic."""

    def __init__(self):
        """Initializes Data class."""

        self._args_details = [
            {'name': Datatype()},
            {'surname': Datatype()},
            {'email': Datatype()},
            {'birthday': Datatype(datatype='date', size=None, null='NULL')},
            {'phone': Datatype(size=100)},
            {'company': Datatype()},
            {'user_id': Datatype(size=13)},
            {'address': Datatype()},
            {'city': Datatype()},
            {'zip': Datatype(size=10)},
            {'region': Datatype(size=50)},
            {'country': Datatype(size=100)},
            {'coordinates': Datatype(size=30)},
            {'cvisa': Datatype(size=50)},
            {'cvisa_cvv': Datatype(size=10)},
            {'cmastercard': Datatype(size=50)},
            {'cmastercard_cvv': Datatype(size=10)},
            {'username': Datatype()},
            {'password': Datatype()},
            {'salary': Datatype(size=100)},
            {'children': Datatype(datatype='tinyint', type_options=['unsigned'], size=None)},
            {'price': Datatype(size=100)},
            {'stock': Datatype(datatype='tinyint', type_options=['unsigned'], size=None)},
            {'contact': Datatype()},
            {'quantity': Datatype(datatype='tinyint', type_options=['unsigned'], size=None)},
            {'date': Datatype(datatype='date', size=None, null='NULL')},
            {'invoice': Datatype(size=10)},
        ]

    @property
    def args(self):
        """Getter for args."""

        return self._args_details

    @args.setter
    def args(self, ls_args):
        """Filter args."""
        args = []

        for arg in ls_args:
            args.append(list(filter(lambda arg_detail: list(arg_detail.keys())[0] == arg, self._args_details))[0])
        self._args_details = args

    def save_data(self, data, fkeys=None, **options):
        """Save data into database."""
        try:
            ws = datagen.Warning_Singleton()
            ws.wprint('Starting database part...', 3)
            table_name = options['table']
            hdb = handle_db(**options['database'])
            db = hdb.open_db()
            if db is None:
                raise MySQLdb._exceptions.DatabaseError('Error accessing database.')
            ws.wprint('Database opened', 2)
            cursor = db.cursor()

            if options['drop'] is True:
                ws.wprint('Dropping ' + table_name + '...', 2)
                sql = 'DROP TABLE IF EXISTS ' + table_name
                hdb.runQuery(sql)

            # Creates a new table
            ws.wprint('Creating ' + table_name + '...', 2)
            sql = 'CREATE TABLE IF NOT EXISTS ' + table_name + '('
            foreign_keys = [];
            if options['id_increment'] is True:
                sql += '`id` mediumint(8) unsigned NOT NULL auto_increment, '

            if fkeys is not None:
                tables_keys = ''
                table_key = ''
                table_tuple = [(re.search('.*(?=__)', fkeys).group(0), re.search('(?<=__).*$', fkeys).group(0)) for fkeys in fkeys]  # noqa:E501
                fkeys_types = {}
                for table, key in table_tuple:
                    sql2 = f'describe {table}'
                    result = hdb.runQuery(sql2)
                    if len([item for item in result if item[0] == key]) == 0:
                        raise AttributeError(f"Error with '{table}__{key}' in {table_name}")
                    found_key = [item for item in result if item[0] == key][0]
                    fkeys_types[f'{table}__{key}'] = found_key[1]
                    table_key = table + '__' + found_key[0]
                    tables_keys += table_key + ', '
                    foreign_keys.append(f'FOREIGN KEY ({table}__{key}) REFERENCES {table}({key}) ON DELETE SET NULL')

                    sql += f'`{table_key}` {found_key[1]} NULL, '

            for col in self._args_details:
                column_name = list(col.keys())[0]
                datatype = col[column_name].datatype
                size = col[column_name].size
                type_options = ' '.join(col[column_name].type_options)
                null = col[column_name].null

                sql += '`' + column_name + '` '
                sql += datatype + ''

                if size is not None:
                    sql += '(' + str(size) + ') '
                else:
                    sql += ' '
                sql += type_options + ' '
                sql += null + ', '

            if options['id_increment'] is True:
                sql += 'PRIMARY KEY (`id`)'
            else:
                sql = sql[:-2]
            sql += ', ' + ', '.join(foreign_keys) if len(foreign_keys) > 0 else '';
            sql += ')'
            hdb.runQuery(sql)

            # Inserts data into the newly created table
            ws.wprint('Inserting data into ' + table_name + '...', 2)
            sql = 'INSERT INTO ' + table_name + '('
            if fkeys is not None:
                sql += tables_keys
            sql += ', '.join([list(item.keys())[0] for item in self._args_details]) + ') '  # noqa:E501
            sql += 'VALUES'

            for row in data:
                strrow = list(map(lambda r: ("'" + r + "'") if isinstance(r, str) else str(r), row))  # noqa:E501
                sql += '('

                if fkeys is not None:
                    for table, key in table_tuple:
                        sql2 = f'SELECT {key} FROM {table} ORDER BY RAND() LIMIT 1'
                        rand_value = hdb.runQuery(sql2, {'fetchone': True})[0]
                        quote = "'" if fkeys_types[f'{table}__{key}'][:7] == 'varchar' else ''
                        sql += quote + str(rand_value) + quote + ', '

                sql += ', '.join(strrow) + '),'
            sql = sql[:-1]

            # cursor.execute(sql)
            hdb.runQuery(sql)
            db.commit()
            ws.wprint('Insert completed successfully', 3)
        except (MySQLdb.OperationalError) as e:
            ws.sh_exc(sys.exc_info(), e)
            ws.wprint('Rolling back...', 3)
            db.rollback()
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)
        else:
            hdb.close_db()
        finally:
            ws.wprint('Database part finalized', 3)
