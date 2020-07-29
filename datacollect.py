"""Data collector."""

import getopt
import json
import sys
import os
import pwd

from populate import datagen


def usage(*args, **kwargs):
    """Usage function."""
    print('Usage:', sys.argv[0], '[OPTIONS]')

    usage_general = {
        '    --help': 'Shows this help',
        '-i, --input': 'Loads json file with structure',
        '-v[vv]': 'Verbosity (up to 3 levels). Default is 1',
        '-q, --quiet': 'Quiet mode, overrides -v',
        '    --drop_if_exists': 'Drops the tables before creating them',
        '    --id_increment': 'Creates `id` primary key for tables (can be overwritten by specific id_increment)',
    }
    usage_database = {
        '-h, --host': 'Host used for database connection. Default is localhost.',
        '-u, --username=user': 'Username used for database connection. Current user is default (must have privileges to create / insert)',  # noqa:E501
        '-p, --password=pass': 'Password used for database connection. Default is Blank',
        '-d, --database=database': "Database name used for database connection. Default is 'test'",
    }
    usage_tables = {
        '-t, --table=table': 'table(s) and options. Check TABLES section for details',
        '-x, --transaction=transaction': 'transaction(s) and options. Check TABLES section for detail.',
    }
    notes = {
        'GENERAL NOTES': 'Table data can be informed in the command line or in a separate JSON file. If the same item is specified in both places, the command line takes precedence. If the table options (drop_if_exists and id_increment) are not specified anywhere, the default values will be used. If table columns are specified in both the command line and the separate JSON file, all of the fields will be used (caution: duplicated field names will cause errors)',  # noqa:E501
        'TABLES': 'Tables represent a list of items to allow the program to create and populate tables in the database. One `-t` or `--tables` option can contain one or more set of items for tables. You can specify all the tables in one `-t` or `--tables` option or multiple options for one or more table (using semi-colon (;) as a separator). It can be written in a JSON format or in a list of items separated by specific characters.\n\n    For the list in specific format it must be like this:\n        table_name:quantity:drop_if_exists:id_increment:column1,column2,column3:extra\n\n    The JSON fields are:\n        {"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "extra": ["extra_option"], "items": ["column1", "column2", "column3"]}\n\n    Check examples at the end.',  # noqa:E501
        'TRANSACTIONS': 'Transactions, similar to tables, represent a list of items to allow the program to create and populate specifc tables called, here in this program, transactions. Those specific tables are tables which have some foreigner key from another table. As a common example, a store may have a table for product and a table for customers. But when a customer purchases a product, this purchase is usually registered in a third table containing some reference to the other two tables. For the foreigner keys, they must be indicated along with their origin tables. The examples show how they work. One `-x` or `--transactions` option can contain one or more set of items for transactions. You can specify all the transactions in one `-x` or `--transactions` option or multiple options for one or more transactions. It can be written in a JSON format or in a list of items separated by specific characters.\n\n    For the list in specific format it must be like this:\n    table_name:quantity:drop_if_exists:id_increment:foreigner_table__foreigner_column, foreigner_table2__foreigner_column,column1,column2,column3\n\n    The JSON fields are:\n    {"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "items": [{"foreigner_table_name": "foreigner_key"}, {"foreigner_table_name": "foreigner_key"}, "column1", "column2", "column3"]}}\n\n    Check examples at the end.',  # noqa:E501
        'EXAMPLES': ' Creates tables customers and products and a transaction table sales (customers x products):\n' +  # noqa:E501,W504
        f'    $ python {sys.argv[0]}' + ' -vv -u dbuser -p dbpass -d test -t customers:20:true:true:name,surname,city,region,country -t sales_dept:8:true:true:name:surname:user_id:salary -t products:50:true:true:stock,price:product -x sales:70:false:true:customers__id,products__id,quantity,date,invoice\n\n' +  # noqa:E501,W504
        '    - Explanation: This will create two tables: customers and products, and one transaction table: sales. The transaction sales will reference the id columns in both customers and products, so, those fields must exist in those tables. The table and the column are separated by two underscore (__). That is guaranteed by the second true after the table name. Notice the string `product` as the last item products listing. This allows the program to get the procut names from another source than the rest. Because the name of the product is fetched automatically, it is not specificed in the item list.\n\n' +  # noqa:E501,W504
        '    The same line in JSON format would be:\n' +  # noqa:E501,W504
        f'    $ python {sys.argv[0]}' + """ -vv -u dbuser -p dbpass -d test --drop_if_exists -t '{"customers": {"quantity": 70, "items": ["name", "surname", "children", "birthday", "city", "address"]}}' -t '{"sales_dept": {"quantity": 8, "id_increment": true, "items": ["name", "surname", "user_id", "salary"]}}' -t '{"products": {"quantity": 70, "drop_if_exists": true, "extra": ["product"],"items": ["stock", "price"]}}' -x '{"sales": {"quantity": 80, "drop_if_exists": true, "items": [{"customers": "id"}, {"products": "name"}, {"sales_dept": "id"}, "quantity", "date", "invoice"]}}'\n\n""" +  # noqa:E501,W504
        '    - Explanation: This has the same effect as the previous example but it uses JSON format for the `-t` and `-x` options. The main difference is that the options like drop_if_exists and id_increment are optional here, meaning the program will assume default values if they are not present globally by the use of --drop_if_exists or --id_increment or if the options are not present in the json file.',  # noqa:E501,W504
    }
    usage_help = {
        'General': usage_general,
        'Database': usage_database,
        'Tables and Transactions': usage_tables,
        'notes': notes,
    }

    min_col = 20
    col_width = max([len(opt[0]) for opt in kwargs['opts']]) + min_col  # noqa:C407
    print()
    for key, item in usage_help.items():
        print('  ' + key)
        for row in list(item.items()):
            if key != 'notes':
                print('   ', row[0].ljust(col_width), row[1])
            else:
                print()
                print(row[0])
                print('   ' + row[1])


def main():
    """Main function."""
    ws = datagen.Warning_Singleton()
    try:
        err = datagen.Error()
        opts = None
        args = None
        jsonfile = None
        data = None

        # Global vars
        verbosity = None
        quiet = None
        gvars = {
            'host': {'current': None, 'default': 'localhost'},
            'username': {'current': None, 'default': pwd.getpwuid(os.getuid()).pw_name},
            'password': {'current': None, 'default': ''},
            'database': {'current': None, 'default': 'test'},
            'drop_if_exists': {'current': None, 'default': False},
            'id_increment': {'current': None, 'default': True},
        }
        tvars = []

        defopts = ['help', 'input=', 'quiet', 'host=', 'username=', 'password=', 'database=', 'drop_if_exists', 'id_increment', 'table', 'transaction']  # noqa:E501
        opts, args = getopt.getopt(sys.argv[1:], 'i:vqh:u:p:d:t:x:', defopts)
        if opts == []:
            usage(opts=defopts)
            sys.exit(err.error)
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
            elif o in ['-u', '--username']:
                if gvars['username']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['username']['current'] = v
            elif o in ['-p', '--password']:
                if gvars['password']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['password']['current'] = v
            elif o in ['-d', '--database']:
                if gvars['database']['current'] is not None:
                    raise getopt.GetoptError('duplicated option: ' + o)
                gvars['database']['current'] = v
            elif o in ['--drop_if_exists']:
                gvars['drop_if_exists']['current'] = True
            elif o in ['--id_increment']:
                gvars['id_increment']['current'] = True
            elif o in ['-t', '--table']:
                tvars.append('tables:' + v)
            elif o in ['-x', '--transaction']:
                tvars.append('transactions:' + v)
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
            data['database'][item] = obj['default'] if obj['current'] is None else obj['current']

        data = datagen.parse_options(tvars, data)

        if verbosity is None:
            verbosity = 1
        if quiet is None:
            quiet = False

        ws.params = (verbosity, quiet)

        ws.wprint('Starting populate...', 0)
        datagen.do_it(**data)

        ws.wprint('', 1)
        ws.wprint(f'Populate finished {"successfuly" if err.error == 0 else "with error"}.', 0)

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
