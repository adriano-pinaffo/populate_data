"""Data collector."""

import getopt
import json
import sys
import os
import pwd

from modules import datagen


def usage(*args, **kwargs):
    """Usage function."""
    print('Usage:', sys.argv[0], '[OPTIONS]')

    usage_commands = {
        'create|mk': 'creates tables and populates them with data (default)',
        'list|ls': 'lists all tables in the database',
        'drop|rm': 'drops tables',
    }
    usage_general = {
        '    --help': 'Shows this help',
        '-i, --input': 'Loads json file with structure',
        '-v[vv]': 'Verbosity (up to 3 levels). Default is 1',
        '-q, --quiet': 'Quiet mode, overrides -v',
    }
    usage_database = {
        '-h, --host': 'Host used for database connection. Default is localhost.',
        '-u, --username=user': 'Username used for database connection. Current user is default (must have privileges to create / insert)',  # noqa:E501
        '-p, --password=pass': 'Password used for database connection. Default is Blank',
        '-d, --database=database': "Database name used for database connection. Default is 'test'",
    }
    usage_create = {
        '    --drop_if_exists': 'Drops the tables before creating them',
        '    --id_increment': 'Creates `id` primary key for tables (can be overwritten by specific id_increment)',
        '-t, --table=table': 'table(s) and options. Check TABLES section for details',
        '-x, --transaction=transaction': 'transaction(s) and options. Check TABLES section for detail.',
    }
    usage_list = {
        '    --no-header': 'Hides the header (applicable only when format is table )',
        '-f, --format=[table,json]': 'Outputs tables in table format (default) or json (string representing json)',
        '-o, --output=path': 'Outputs result to a file',
    }
    usage_drop = {
        '-t, --table=[table1,table2,...]': 'Lists tables to drop, otherwise all tables are dropped',
        '-r, --respect-foreign-keys': 'Respect foreign keys constraint (ignore foreign keys constraints by default)',
        '-y, --yes': 'Reply yes to all',
    }
    notes = {
        'GENERAL NOTES': 'Table data can be informed in the command line or in a separate JSON file. If the same item is specified in both places, the command line takes precedence. If the table options (drop_if_exists and id_increment) are not specified anywhere, the default values will be used. If table columns are specified in both the command line and the separate JSON file, all of the fields will be used (caution: duplicated field names will cause errors)',  # noqa:E501
        'TABLES': 'Tables represent a list of items to allow the program to create and populate tables in the database. One `-t` or `--tables` option can contain one or more set of items for tables. You can specify all the tables in one `-t` or `--tables` option or multiple options for one or more table (using semi-colon (;) as a separator). It can be written in a JSON format or in a list of items separated by specific characters.\n\n    For the list in specific format it must be like this:\n        table_name:quantity:drop_if_exists:id_increment:column1,column2,column3:extra\n\n    The JSON fields are:\n        {"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "extra": ["extra_option"], "items": ["column1", "column2", "column3"]}\n\n    Check examples at the end.',  # noqa:E501
        'TRANSACTIONS': 'Transactions, similar to tables, represent a list of items to allow the program to create and populate specifc tables called, here in this program, transactions. Those specific tables are tables which have some foreigner key from another table. As a common example, a store may have a table for product and a table for customers. But when a customer purchases a product, this purchase is usually registered in a third table containing some reference to the other two tables. For the foreigner keys, they must be indicated along with their origin tables. The examples show how they work. One `-x` or `--transactions` option can contain one or more set of items for transactions. You can specify all the transactions in one `-x` or `--transactions` option or multiple options for one or more transactions. It can be written in a JSON format or in a list of items separated by specific characters.\n\n    For the list in specific format it must be like this:\n    table_name:quantity:drop_if_exists:id_increment:foreigner_table__foreigner_column, foreigner_table2__foreigner_column,column1,column2,column3\n\n    The JSON fields are:\n    {"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "items": [{"foreigner_table": "foreigner_key"}, {"foreigner_table2": "foreigner_key"}, "column1", "column2", "column3"]}}\n\n    Check examples at the end.',  # noqa:E501
        'EXAMPLES': ' Creates tables customers and products and a transaction table sales (customers x products):\n' +  # noqa:E501,W504
        f'    $ python {sys.argv[0]}' + ' -vv -u dbuser -p dbpass -d test -t customers:20:true:true:name,surname,city,region,country -t products:50:true:true:stock,price:product -x sales:70:false:true:customers__id,products__id,quantity,date,invoice\n\n' +  # noqa:E501,W504
        '    - Explanation: This will create two tables: customers and products, and one transaction table: sales. The transaction sales will reference the id columns in both customers and products, so, those fields must exist in those tables. The table and the column are separated by two underscore (__). That is guaranteed by the second true after the table name. Notice the string `product` as the last item products listing. This allows the program to get the procut names from another source than the rest. Because the name of the product is fetched automatically, it is not specificed in the item list.\n\n' +  # noqa:E501,W504
        '    The same line in JSON format would be:\n' +  # noqa:E501,W504
        f'    $ python {sys.argv[0]}' + """ -vv -u dbuser -p dbpass -d test --drop_if_exists -t '{"customers": {"quantity": 70, "items": ["name", "surname", "children", "birthday", "city", "address"]}}' -t '{"sales_dept": {"quantity": 8, "id_increment": true, "items": ["name", "surname", "user_id", "salary"]}}' -t '{"products": {"quantity": 70, "drop_if_exists": true, "extra": ["product"],"items": ["stock", "price"]}}' -x '{"sales": {"quantity": 80, "drop_if_exists": true, "items": [{"customers": "id"}, {"products": "name"}, {"sales_dept": "id"}, "quantity", "date", "invoice"]}}'\n\n""" +  # noqa:E501,W504
        '    - Explanation: This has the same effect as the previous example but it uses JSON format for the `-t` and `-x` options. The main difference is that the options like drop_if_exists and id_increment are optional here, meaning the program will assume default values if they are not present globally by the use of --drop_if_exists or --id_increment or if the options are not present in the json file.',  # noqa:E501,W504
        'FIELDS': """name         field representing first name
surname         field representing last name
email           field representing an email address
birthday        will populate field with date information
phone           field representing a phone number
company         will populate with company names
user_id         field representing a user identification
address         will populate with home/business address
city            will populate with city names (not in sync with region for country)
region          will populate with region names (State or Province) (not in sync with city or country)
country         will populate with country names (not in sync with city or region)
coordinates     will populate with latitude and longitude
cvisa           represents a visa card (credit)
cvisa_cvv       represents the visa card verification value
cmastercard     represents a mastercard card (credit)
cmastercard_cvv represents the mastercard card verification value
username        will populate with usernames (first leter of name plus surname)
password        will populate with random password strings
salary          an amount that represents a salary
children        an integer representing the number of children of a person
price           an amount representing the price of a product
stock           an integer representing the product availability
contact         field representing someone's contact
quantity        an integer representing some quantity (amount of products sold, for exemple)
date            a date field (similar to birthday)
invoice         an integer representing an invoice number""",
        'LIMITATIONS': 'This program will download at most 100 items at a time. Future releases may change that.\nThe column name in the database has exactly the same name of the field indicated in the JSON file. Future releases may decouple the name of the column and the field in the JSON file.\n   This program is partially based on generatedata.com (older v3 version), which will be available until Dec 31, 2026',  # noqa:E501
        'CONTACT': 'Contact the author or inform bugs by using the github repository of this project at https://github.com/adriano-pinaffo/populate_data',  # noqa:E501
    }
    usage_help = {
        'Commands': usage_commands,
        'General': usage_general,
        'Database': usage_database,
        'Create Options': usage_create,
        'List Options': usage_list,
        'Drop Options': usage_drop,
        'Notes': notes,
    }

    keys = []
    keys_sections = [key for key in [list(item.keys()) for item in [usage_help[opt] for opt in usage_help]]]
    for items in keys_sections:
        keys += items
    col_width = max([len(item) for item in keys])
    # col_width = max([len(opt[0]) for opt in kwargs['opts']]) + min_col  # noqa:C407
    for key, item in usage_help.items():
        print('  \n' + key)
        for row in list(item.items()):
            if key != 'Notes':
                print('  ', row[0].ljust(col_width), row[1])
            else:
                print()
                print(row[0])
                print('    ' + row[1])


def main():
    """Main function."""
    ws = datagen.Warning_Singleton()
    try:
        err = datagen.Error()
        opts = None
        args = None
        jsonfile = None
        data = None
        command = 'create'

        # Global vars
        verbosity = None
        quiet = None
        gvars = {
            'host': {'current': None, 'default': 'localhost', 'set': False},
            'username': {'current': None, 'default': pwd.getpwuid(os.getuid()).pw_name, 'set': False},
            'password': {'current': None, 'default': '', 'set': False},
            'database': {'current': None, 'default': 'test', 'set': False},
            'drop_if_exists': {'current': None, 'default': False, 'set': False},
            'id_increment': {'current': None, 'default': True, 'set': False},
        }
        tvars = []
        lvars = {
            'header': True,
            'format': 'table',
            'output': None,
        }
        dvars = {
            'table': None,
            'respectForeignKeys': False,
            'yesAll': False,
        }

        sys_args = sys.argv[1:];
        if len(sys_args) == 0:
            usage()
            sys.exit(err.error)

        if sys_args[0] == 'create' or sys_args[0] == 'mk':
            command = 'create'
            sys_args = sys_args[1:];
        elif sys_args[0] == 'list' or sys_args[0] == 'ls':
            command = 'list'
            sys_args = sys_args[1:];
        elif sys_args[0] == 'drop' or sys_args[0] == 'rm':
            command = 'drop'
            sys_args = sys_args[1:];

        defopts = [
            'help',
            'input=',
            'quiet',
            'host=',
            'username=',
            'password=',
            'database=',
            'drop_if_exists',
            'id_increment',
            'table',
            'transaction',
            'no-header',
            'format=',
            'output=',
            'respect-foreign-keys',
            'yes',
        ]
        opts, args = getopt.getopt(sys_args, 'i:vqh:u:p:d:t:x:f:o:ry', defopts)
        for o, v in opts:
            if o in ['--help']:
                usage(opts=defopts)
                sys.exit(err.error)
            elif o in ['-i', '--input']:
                jsonfile = v
            elif o in ['-v']:
                if verbosity is None:
                    verbosity = 0
                verbosity += 1
                if verbosity > 3:
                    raise getopt.GetoptError('Verbosity out of bound')
            elif o in ['-q', '--quiet']:
                quiet = True
            elif o in ['-h', '--host']:
                if gvars['host']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['host']['current'] = v
                gvars['host']['set'] = True
            elif o in ['-u', '--username']:
                if gvars['username']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['username']['current'] = v
                gvars['username']['set'] = True
            elif o in ['-p', '--password']:
                if gvars['password']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['password']['current'] = v
                gvars['password']['set'] = True
            elif o in ['-d', '--database']:
                if gvars['database']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['database']['current'] = v
                gvars['database']['set'] = True
            elif o in ['--drop_if_exists']:
                gvars['drop_if_exists']['current'] = True
                gvars['drop_if_exists']['set'] = True
            elif o in ['--id_increment']:
                gvars['id_increment']['current'] = True
                gvars['id_increment']['set'] = True
            elif o in ['-t', '--table']:
                if command == 'create':
                    tvars.append('tables:' + v)
                elif command == 'drop':
                    dvars['table'] = v.split(',')
            elif o in ['-x', '--transaction']:
                tvars.append('transactions:' + v)
            elif o in ['--no-header']:
                lvars['header'] = False
            elif o in ['-f', '--format']:
                lvars['format'] = v
            elif o in ['-o', '--output']:
                lvars['output'] = v
            elif o in ['-r', '--respect-foreign-keys']:
                dvars['respectForeignKeys'] = True
            elif o in ['-y', '--yes']:
                dvars['yesAll'] = True
            else:
                raise AssertionError('unhandled option')

        if jsonfile is not None:
            with open(jsonfile, 'r') as file:
                data = json.load(file)

        if data is None:
            data = {}
        if data.get('database') is None:
            data['database'] = {}
        if data.get('tables') is None:
            data['tables'] = []
        if data.get('transactions') is None:
            data['transactions'] = []

        for item, obj in gvars.items():
            if item in data['database']:
                data['database'][item] = obj['current'] if obj['set'] is True else data['database'][item]
            else:
                data['database'][item] = obj['current'] if obj['set'] is True else obj['default']

        data = datagen.parse_options(tvars, data)
        data['list_options'] = lvars
        data['drop_options'] = dvars

        if verbosity is None:
            verbosity = 1
        if quiet is None:
            quiet = False

        ws.params = (verbosity, quiet)

        if command == 'create':
            ws.wprint('Starting populate...', 0)
            datagen.do_it(**data)

            ws.wprint('', 1)
            ws.wprint(f'Populate finished {"successfuly" if err.error == 0 else "with error"}.', 0)
        elif command == 'list':
            datagen.do_list(**data)
        elif command == 'drop':
            datagen.do_drop(**data)

    except getopt.GetoptError as e:
        ws.sh_exc(sys.exc_info(), e)
        usage(opts=defopts)
    except BaseException as e:
        if sys.exc_info()[0].__name__ != 'SystemExit':
            ws.sh_exc(sys.exc_info(), e)
    finally:
        sys.exit(err.error)


if __name__ == '__main__':
    main()
