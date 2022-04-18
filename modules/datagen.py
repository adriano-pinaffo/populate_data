"""Parameters."""
import sys
import os
import requests
import datetime
import random
import re
import json
from modules import database


class Post_Creator():
    """Connection to generatedata.com."""

    def __init__(self, **kwargs):
        """Initialize the class."""
        self._url = 'https://generatedata3.com/ajax.php'
        self._headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'http://generatedata.com',
            'Connection': 'keep-alive',
            'Referer': 'http://generatedata.com/',
        }
        self._data = {
            'gdExportType': 'JSON',
            'gdNumCols': '4',
            'gdExportFormat': '',
            'configurationID': '',
            'gdNumRowsToAdd': '1',
            'gdNumRowsToGenerate': '100',
            'gdExportTarget': 'inPage',
            'action': 'generateInPage',
            'gdBatchSize': '100',
            'gdCurrentBatchNum': '1',
        }

        if kwargs['row_qty'] is not None:
            self._data['gdNumRowsToGenerate'] = kwargs['row_qty']
        self.enter_data(kwargs['al'])

    def enter_data(self, args_list):
        """Enter additional params."""

        self.params = []

        for i, item in enumerate(args_list):
            for subitem in item[list(item.keys())[0]]:
                self._data[subitem + ('_' if subitem[:8] != 'dtLatLng' else '') + str(i + 1)] = item[list(item.keys())[0]][subitem]  # noqa:E501

        self._data['gdRowOrder'] = ''

        for i in range(1, len(args_list) + 1):
            self._data['gdRowOrder'] += str(i) + ','
        self._data['gdRowOrder'] = self._data['gdRowOrder'][:-1]

    @property
    def data(self):
        """Returns data."""

        return self._data

    @property
    def url(self):
        """Returns url."""

        return self._url

    @property
    def headers(self):
        """Returns Headers."""

        return self._headers


class Param_Creator():
    """Class to create parameters."""

    def __init__(self, list_params=None):
        """Initializes Param_Creator."""

        self.all_params = [
            {'name': {
                'gdTitle': 'name',
                'gdDataType': 'data-type-Names',
                'dtOption': 'Name',
                'dtExample': 'Name'}},
            {'surname': {
                'gdTitle': 'surname',
                'gdDataType': 'data-type-Names',
                'dtOption': 'Surname',
                'dtExample': 'Surname'}},
            {'email': {
                'gdTitle': 'email',
                'gdDataType': 'data-type-Email'}},
            {'birthday': {
                'gdTitle': 'birthday',
                'gdDataType': 'data-type-Date',
                'dtOption': 'Y-m-d',
                'dtFromDate': '01/01/1910',
                'dtToDate': datetime.datetime.now().strftime('%m/%d/%Y')}},
            {'phone': {
                'gdTitle': 'phone',
                'gdDataType': 'data-type-Phone',
                'dtOption': '1-Xxx-Xxx-xxxx',
                'dtExample': '1-Xxx-Xxx-xxxx'}},
            {'company': {
                'gdTitle': 'company',
                'gdDataType': 'data-type-Company'}},
            {'user_id': {
                'gdTitle': 'user_id',
                'gdDataType': 'data-type-PersonalNumber',
                'dtOption': 'PersonalNumberWithoutHyphen',
                'dtOptionPersonalNumber_sep': ''}},
            {'address': {
                'gdTitle': 'address',
                'gdDataType': 'data-type-StreetAddress'}},
            {'city': {
                'gdTitle': 'city',
                'gdDataType': 'data-type-City'}},
            {'zip': {
                'gdTitle': 'zip',
                'gdDataType': 'data-type-PostalZip',
                'dtCountryIncludeZip_australia': 'on',
                'dtCountryIncludeZip_austria': 'on',
                'dtCountryIncludeZip_belgium': 'on',
                'dtCountryIncludeZip_brazil': 'on',
                'dtCountryIncludeZip_CA': 'on',
                'dtCountryIncludeZip_chile': 'on',
                'dtCountryIncludeZip_CR': 'on',
                'dtCountryIncludeZip_france': 'on',
                'dtCountryIncludeZip_germany': 'on',
                'dtCountryIncludeZip_india': 'on',
                'dtCountryIncludeZip_ireland': 'on',
                'dtCountryIncludeZip_italy': 'on',
                'dtCountryIncludeZip_netherlands': 'on',
                'dtCountryIncludeZip_newzealand': 'on',
                'dtCountryIncludeZip_nigeria': 'on',
                'dtCountryIncludeZip_poland': 'on',
                'dtCountryIncludeZip_spain': 'on',
                'dtCountryIncludeZip_sweden': 'on',
                'dtCountryIncludeZip_turkey': 'on',
                'dtCountryIncludeZip_united_kingdom': 'on',
                'dtCountryIncludeZip_US': 'on',
                'dtCountryIncludeZip_colombia': 'on',
                'dtCountryIncludeZip_indonesia': 'on',
                'dtCountryIncludeZip_mexico': 'on',
                'dtCountryIncludeZip_pakistan': 'on',
                'dtCountryIncludeZip_peru': 'on',
                'dtCountryIncludeZip_RU': 'on',
                'dtCountryIncludeZip_southkorea': 'on'}},
            {'region': {
                'gdTitle': 'region',
                'gdDataType': 'data-type-Region',
                'dtIncludeRegion_australia': 'on',
                'dtIncludeRegion_australia_Full': 'on',
                'dtIncludeRegion_australia_Short': 'on',
                'dtIncludeRegion_austria': 'on',
                'dtIncludeRegion_austria_Full': 'on',
                'dtIncludeRegion_austria_Short': 'on',
                'dtIncludeRegion_belgium': 'on',
                'dtIncludeRegion_belgium_Full': 'on',
                'dtIncludeRegion_belgium_Short': 'on',
                'dtIncludeRegion_brazil': 'on',
                'dtIncludeRegion_brazil_Full': 'on',
                'dtIncludeRegion_brazil_Short': 'on',
                'dtIncludeRegion_CA': 'on',
                'dtIncludeRegion_CA_Full': 'on',
                'dtIncludeRegion_CA_Short': 'on',
                'dtIncludeRegion_chile': 'on',
                'dtIncludeRegion_chile_Full': 'on',
                'dtIncludeRegion_chile_Short': 'on',
                'dtIncludeRegion_CR': 'on',
                'dtIncludeRegion_CR_Full': 'on',
                'dtIncludeRegion_CR_Short': 'on',
                'dtIncludeRegion_france': 'on',
                'dtIncludeRegion_france_Full': 'on',
                'dtIncludeRegion_france_Short': 'on',
                'dtIncludeRegion_germany': 'on',
                'dtIncludeRegion_germany_Full': 'on',
                'dtIncludeRegion_germany_Short': 'on',
                'dtIncludeRegion_india': 'on',
                'dtIncludeRegion_india_Full': 'on',
                'dtIncludeRegion_india_Short': 'on',
                'dtIncludeRegion_ireland': 'on',
                'dtIncludeRegion_ireland_Full': 'on',
                'dtIncludeRegion_ireland_Short': 'on',
                'dtIncludeRegion_italy': 'on',
                'dtIncludeRegion_italy_Full': 'on',
                'dtIncludeRegion_italy_Short': 'on',
                'dtIncludeRegion_netherlands': 'on',
                'dtIncludeRegion_netherlands_Full': 'on',
                'dtIncludeRegion_netherlands_Short': 'on',
                'dtIncludeRegion_newzealand': 'on',
                'dtIncludeRegion_newzealand_Full': 'on',
                'dtIncludeRegion_newzealand_Short': 'on',
                'dtIncludeRegion_nigeria': 'on',
                'dtIncludeRegion_nigeria_Full': 'on',
                'dtIncludeRegion_nigeria_Short': 'on',
                'dtIncludeRegion_poland': 'on',
                'dtIncludeRegion_poland_Full': 'on',
                'dtIncludeRegion_poland_Short': 'on',
                'dtIncludeRegion_spain': 'on',
                'dtIncludeRegion_spain_Full': 'on',
                'dtIncludeRegion_spain_Short': 'on',
                'dtIncludeRegion_sweden': 'on',
                'dtIncludeRegion_sweden_Full': 'on',
                'dtIncludeRegion_sweden_Short': 'on',
                'dtIncludeRegion_turkey': 'on',
                'dtIncludeRegion_turkey_Full': 'on',
                'dtIncludeRegion_turkey_Short': 'on',
                'dtIncludeRegion_united_kingdom': 'on',
                'dtIncludeRegion_united_kingdom_Full': 'on',
                'dtIncludeRegion_united_kingdom_Short': 'on',
                'dtIncludeRegion_US': 'on',
                'dtIncludeRegion_US_Full': 'on',
                'dtIncludeRegion_US_Short': 'on',
                'dtIncludeRegion_colombia': 'on',
                'dtIncludeRegion_colombia_Full': 'on',
                'dtIncludeRegion_colombia_Short': 'on',
                'dtIncludeRegion_indonesia': 'on',
                'dtIncludeRegion_indonesia_Full': 'on',
                'dtIncludeRegion_indonesia_Short': 'on',
                'dtIncludeRegion_mexico': 'on',
                'dtIncludeRegion_mexico_Full': 'on',
                'dtIncludeRegion_mexico_Short': 'on',
                'dtIncludeRegion_pakistan': 'on',
                'dtIncludeRegion_pakistan_Full': 'on',
                'dtIncludeRegion_pakistan_Short': 'on',
                'dtIncludeRegion_peru': 'on',
                'dtIncludeRegion_peru_Full': 'on',
                'dtIncludeRegion_peru_Short': 'on',
                'dtIncludeRegion_RU': 'on',
                'dtIncludeRegion_RU_Full': 'on',
                'dtIncludeRegion_RU_Short': 'on',
                'dtIncludeRegion_southkorea': 'on',
                'dtIncludeRegion_southkorea_Full': 'on',
                'dtIncludeRegion_southkorea_Short_8': 'on'}},
            {'country': {
                'gdTitle': 'country',
                'gdDataType': 'data-type-Country'}},
            {'coordinates': {
                'gdTitle': 'coordinates',
                'gdDataType': 'data-type-LatLng',
                'dtLatLng_Lat': 'on',
                'dtLatLng_Lng': 'on'}},
            {'cvisa': {
                'gdTitle': 'cvisa',
                'gdDataType': 'data-type-PAN',
                'dtExample': 'visa',
                'dtOptionPAN_digit': '13,16',
                'dtOptionPAN_sep': '-',
                'dtOption': 'XXXXXXXXXXXXXXXXX+XXX+XX+XXXXXXXXXXXXXXXXXXXXXXXX+XXXX+XXXX+XXXXXXXXXX+XXXXXX+XXXXXXX+XXXXX+XXXXX+XXXXXXXXX+XXXXXXXXXX'}},  # noqa:E501
            {'cvisa_cvv': {
                'gdTitle': 'cvisa_cvv',
                'gdDataType': 'data-type-CVV'}},
            {'cmastercard': {
                'gdTitle': 'cmastercard',
                'gdDataType': 'data-type-PAN',
                'dtExample': 'mastercard',
                'dtOptionPAN_digit': '16',
                'dtOptionPAN_sep': '+',
                'dtOption': 'XXXXXXXXXXXXXXXXXXXX+XXXX+XXXX+XXXXXXXXXX+XXXXXX+XXXXXXX+XXXXX+XXXXX+XXXXXXXXX+XXXXXXXXXX'}},  # noqa:E501
            {'cmastercard_cvv': {
                'gdTitle': 'cmastercard_cvv',
                'gdDataType': 'data-type-CVV'}},
            {'username': {
                'gdTitle': 'username',
                'gdDataType': 'data-type-Names',
                'dtExample': 'Name',
                'dtOption': 'Name.Surname'}},
            {'password': {
                'gdTitle': 'password',
                'gdDataType': 'data-type-AlphaNumeric',
                'dtExample': 'LLLxxLLLxLL',
                'dtOption': 'LLLxxLLLxLL'}},
            {'salary': {
                'gdTitle': 'salary',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '1000',
                'dtNumRangeMax': '100000'}},
            {'children': {
                'gdTitle': 'children',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '0',
                'dtNumRangeMax': '5'}},
            {'price': {
                'gdTitle': 'price',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '10',
                'dtNumRangeMax': '500'}},
            {'stock': {
                'gdTitle': 'stock',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '0',
                'dtNumRangeMax': '100'}},
            {'contact': {
                'gdTitle': 'contact',
                'gdDataType': 'data-type-Names',
                'dtOption': 'Name+Surname|Name+Initial.+Surname',
                'dtExample': '"Name+Surname|Name+Initial.+Surname"'}},
            {'quantity': {
                'gdTitle': 'quantity',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '0',
                'dtNumRangeMax': '20'}},
            {'date': {
                'gdTitle': 'date',
                'gdDataType': 'data-type-Date',
                'dtOption': 'Y-m-d',
                'dtFromDate': '01/01/1990',
                'dtToDate': datetime.datetime.now().strftime('%m/%d/%Y')}},
            {'invoice': {
                'gdTitle': 'invoice',
                'gdDataType': 'data-type-NumberRange',
                'dtNumRangeMin': '100',
                'dtNumRangeMax': '3000'}},
        ]

        # Filters for params entered by calling program

        if list_params is not None:
            filtered_params = list(filter(lambda param: list(param.keys())[0] in list_params, self.all_params))
            self.all_params = []

            # Reorder params based on list coming from calling program

            for param in list_params:
                self.all_params.append(list(filter(lambda item: list(item.keys())[0] == param, filtered_params))[0])

    @property
    def args_list(self):
        """Returns the list of arguments."""

        return self.all_params


class Product_Prepare():
    """Methods for products."""

    def __init__(self):
        """Initialize Product_Prepare class."""
        pass

    def get_product_list(self, resp, qty):
        """Return list of products from request."""
        all_products = resp.json()['RandL']['items']
        products = []

        for _i in range(0, qty):
            rand = random.randint(0, len(all_products) - 1)
            products.append(all_products[rand])
            all_products.remove(all_products[rand])

        return products

    def merge_product(self, prod, proddetail):
        """Merge product list and product detail list."""
        products = []

        for product, product_detail in zip(prod, proddetail):
            products.append([product] + product_detail)

        return products


class Warning_Singleton():
    """Class to deal with messages."""

    verbosity = None
    quiet = None

    def __init__(self, *args, **kwargs):
        """Initialize class warning."""
        if Warning_Singleton.verbosity is None:
            Warning_Singleton.verbosity = kwargs.get('verbosity')
            if Warning_Singleton.verbosity is None:
                Warning_Singleton.verbosity = 1
        if Warning_Singleton.quiet is None:
            Warning_Singleton.quiet = kwargs.get('quiet')
            if Warning_Singleton.quiet is None:
                Warning_Singleton.quiet = False

    @property
    def params(gself):
        """Return verbosity and quiet."""
        return (Warning_Singleton.verbosity, Warning_Singleton.quiet)

    @params.setter
    def params(self, pars):
        """Set verbosity and quiet."""
        Warning_Singleton.verbosity = pars[0]
        Warning_Singleton.quiet = pars[1]

    def wprint(self, mess, verb):
        """Prints message to screen."""
        if Warning_Singleton.quiet is True:
            return 0
        if verb <= Warning_Singleton.verbosity:
            print(mess)

    def eprint(self, mess):
        """Prints error message to stderr."""
        sys.stderr.write(f'{mess}\n')
        err = Error()
        err.error = 1

    def sh_exc(self, exc_info, e):
        """Deals with exception."""
        ws = Warning_Singleton()
        err = Error()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ws.eprint(f'Error occurred: {e}\n    Type {exc_type}\n    File: {fname}\n    Line: {exc_tb.tb_lineno}')
        err.error = 1


class Error():
    """Class Error."""

    errnumber = 0

    @property
    def error(self):
        """Property method error number."""
        return Error.errnumber

    @error.setter
    def error(self, err):
        """Property method error number."""
        Error.errnumber = err


def data_preparation(data=None):
    """Formats returned data."""

    if (data is None):
        return {}
    data_prepared = (data.text
                     .replace('\\t', '')
                     .replace('\\n', '')
                     .replace('\\"', '"')
                     .replace('"{', '{')
                     .replace('}"', '}')
                     .replace("'", ' ')
                     .replace('true', 'True')
                     .replace('false', 'False'))
    data_prepared = re.sub(r'\\u....', '', data_prepared)

    return eval(data_prepared)['content']['data']


def do_it(**all):
    """Main function."""
    db = all['database']
    tbs = all['tables']
    do_tables(tbs, db)

    txs = all['transactions']
    do_tables(txs, db)


def do_tables(tbs, db):
    """Tables function."""

    ws = Warning_Singleton()

    for tb in tbs:
        try:
            ws.wprint('', 1)
            fkeys = None
            selected_params = tb[list(tb.keys())[0]]['items']
            table_name = list(tb.keys())[0]
            ws.wprint('Populating ' + table_name + '...', 1)

            # Singling out tables from transactions
            if type(selected_params[0]).__name__ == 'dict':
                ws.wprint('Generating FKeys...', 3)
                fkeys = list(map(lambda key: list(key.keys())[0] + '__' + key[list(key.keys())[0]], list(filter(lambda item: type(item).__name__ == 'dict', selected_params))))  # noqa:E501
                ws.wprint('Selected FKeys: ' + str(fkeys), 3)
            selected_params = list(filter(lambda item: type(item).__name__ == 'str', selected_params))
            ws.wprint('To download: ' + str(selected_params), 3)

            ws.wprint('Preparing parameters for download...', 3)
            args = Param_Creator(list_params=selected_params)
            args_list = args.args_list
            qty = tb[list(tb.keys())[0]]['quantity']

            drop = tb[list(tb.keys())[0]].get('drop_if_exists')
            if drop is None:
                drop = db.get('drop_if_exists')

            id_increment = tb[list(tb.keys())[0]].get('id_increment')
            if id_increment is None:
                id_increment = db.get('id_increment')

            ws.wprint('Preparing POST request...', 3)
            params = Post_Creator(al=args_list, row_qty=qty)

            ws.wprint('Downloading ' + table_name + '...', 2)
            resp = requests.post(params.url, data=params.data, headers=params.headers, timeout=5)
            if (resp.status_code != 200):
                raise ConnectionError
            ws.wprint('Downloaded', 3)

            ws.wprint('Preparing data...', 3)
            data = data_preparation(resp)

            extra = tb[list(tb.keys())[0]].get('extra')
            if extra is not None:
                if 'product' in extra:
                    ws.wprint('Preparing for product names...', 3)
                    querystring = {'show_images': 'false', 'dup': 'false', 'qty': qty}
                    baseurl = 'https://www.randomlists.com'
                    url = baseurl + '/data/things.json'
                    header = {'Referer': baseurl + '/things' + '?' + '&'.join([key + '=' + str(querystring[key]) for key in list(querystring.keys())])}  # noqa:E501
                    try:
                        ws.wprint('Downloading produt names...', 2)
                        resp_prod = requests.get(url, params=querystring, headers=header, timeout=5)
                        if resp_prod.status_code != 200:
                            raise BaseException
                        prodprep = Product_Prepare()
                        product_list = prodprep.get_product_list(resp_prod, qty)
                        product_details = data_preparation(resp)
                        ws.wprint('Merging product names with product details...', 3)
                        data = prodprep.merge_product(product_list, product_details)
                        selected_params = ['name'] + selected_params
                    except BaseException as e:
                        ws.sh_exc(sys.exc_info(), e)

            do_db_stuff(
                data=data,
                fkeys=fkeys,
                selected_params=selected_params,
                table_name=table_name,
                drop=drop,
                id_increment=id_increment,
                db=db,
            )
        except ConnectionError as e:
            ws.sh_exc(sys.exc_info(), e)
        except BaseException as e:
            ws.sh_exc(sys.exc_info(), e)


def do_db_stuff(**kwargs):
    """Handles db activities."""

    data = kwargs['data']
    selected_params = kwargs['selected_params']
    table_name = kwargs['table_name']
    drop = kwargs['drop']
    id_increment = kwargs['id_increment']
    fkeys = kwargs['fkeys']
    db = kwargs['db']

    db_handler = database.Data()
    db_handler.args = selected_params
    db_handler.save_data(
        data,
        fkeys=fkeys,
        **{'table': table_name,
           'drop': drop,
           'id_increment': id_increment,
           'database': db},
    )


def parse_options(args, data):
    """Parse options for tables."""

    ws = Warning_Singleton()
    try:
        for tb_items in args:
            table_name = None
            table_qty = None
            table_drop = None
            table_id = None
            table_items = None
            table_extra = None
            try:
                table = tb_items.split(':')[0]
                tbi = json.loads(re.search(':.*', tb_items)[0][1:])
            except json.JSONDecodeError:
                tbi = tb_items.split(':')
                table_name = tbi[1]
                table_qty = int(tbi[2])
                table_drop = True if tbi[3].upper() == 'TRUE' else False
                table_id = True if tbi[4].upper() == 'TRUE' else False
                table_items = tbi[5].split(',')
                if len(tbi) == 7:
                    table_extra = tbi[6]
                else:
                    table_extra = None
                for i, item in enumerate(table_items):
                    if item.find('__') != -1:
                        table_items[i] = {re.search('^.*(?=__)', item)[0]: re.search('(?<=__).*$', item)[0]}
                data[table].append({table_name: {'quantity': table_qty, 'drop_if_exists': table_drop, 'id_increment': table_id, 'extra': [table_extra], 'items': table_items}})  # noqa:E501
            else:
                data[re.match('[^:]+', tb_items)[0]].append(tbi)
    except BaseException as e:
        ws.sh_exc(sys.exc_info(), e)
    return data

def do_list(**kwargs):
    """Calls db list."""
    ws = Warning_Singleton()
    try:
        db_handler = database.handle_db(**kwargs.get('database'))
        db_handler.list(kwargs.get('list_options'))
    except BaseException as e:
        ws.sh_exc(sys.exc_info(), e)

def do_drop(**kwargs):
    """Calls db drop."""
    ws = Warning_Singleton()
    try:
        db_handler = database.handle_db(**kwargs.get('database'))
        db_handler.drop(kwargs.get('drop_options'))
    except BaseException as e:
        ws.sh_exc(sys.exc_info(), e)
