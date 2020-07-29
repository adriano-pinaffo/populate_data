import sys
import MySQLdb
import re
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
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)

    def open_db(self):
        """Open database."""
        ws = datagen.Warning_Singleton()
        ws.wprint('Opening database...', 3)

        try:
            self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.database)

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

            return True
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
            cursor = db.cursor()

            if options['drop'] is True:
                # Deletes table if it already exists
                ws.wprint('Dropping ' + table_name + '...', 2)
                sql = 'DROP TABLE IF EXISTS ' + table_name
                cursor.execute(sql)

            # Creates a new table
            ws.wprint('Creating ' + table_name + '...', 2)
            sql = 'CREATE TABLE IF NOT EXISTS ' + table_name + '('
            if options['id_increment'] is True:
                sql += '`id` mediumint(8) unsigned NOT NULL auto_increment, '

            if fkeys is not None:
                # from list like ['custormers__id', 'products__id', 'sales_dept__id'],
                # save str before __ in table and after in key
                tables_keys = ''
                table_key = ''
                table_tuple = [(re.search('.*(?=__)', fkeys).group(0), re.search('(?<=__).*$', fkeys).group(0)) for fkeys in fkeys]  # noqa:E501
                fkeys_types = {}
                for table, key in table_tuple:
                    sql2 = f'describe {table}'
                    cursor.execute(sql2)
                    result = cursor.fetchall()
                    if len([item for item in result if item[0] == key]) == 0:
                        raise AttributeError(f"Error with '{table}__{key}' in {table_name}")
                    found_key = [item for item in result if item[0] == key][0]
                    fkeys_types[f'{table}__{key}'] = found_key[1]
                    table_key = table + '__' + found_key[0]
                    tables_keys += table_key + ', '

                    sql += f'`{table_key}` {found_key[1]} NOT NULL, '

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
            sql += ')'
            cursor.execute(sql)

            # Inserts data into the newly created table
            # sql = 'INSERT INTO ' + options['table'] + '(' + ', '.join(data['content']['cols']) + ') '
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
                        cursor.execute(sql2)
                        rand_value = cursor.fetchone()[0]
                        quote = "'" if fkeys_types[f'{table}__{key}'][:7] == 'varchar' else ''
                        sql += quote + str(rand_value) + quote + ', '

                sql += ', '.join(strrow) + '),'
            sql = sql[:-1]

            cursor.execute(sql)
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
