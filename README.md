# populate_data
This project delivers a Python program that populates a database.
The main use-case for this is for people training with relational databases and need to generate random data in tables.
Another use-case is the one for people practicing their programming skills and want to play around with some elements and modules in python.
This project is a personal development that should, in no way, be used in production environments.

This program will randomly download specific data from the Internet and feed tables in a local database. The data sources in the Internet are generatedata.com and randomlists.com.
This program will easily simulate a company database where you may have data from customers, employees, suppliers, cash flows, sales, etc. This means you can create as many tables as you want, from a pre-selected list of fields.
Aside from the regular tables, you can also create 'transactional' tables which, in this context, represent a table that will have have foreigner keys.

For example, you may create a customer table and a product table. A transaction table could be a sales table having information about products sold, with relations to existing custormer and existing products (plus their own fields).
If not using an input file, -t option will contain the table instruction. The program will accept as many -t options as wanted.
Transaction tables are defined in the -x option. As with -t, you can have as many -x options as you want.

Tables and transactions can be indicated in JSON format or in a colon-formated string. Check below to see how to use them.

<br>
<h3>Populating 1 table with JSON-formatted </h3>
<br><img src="readme_files/populate_1table_json.gif" width=700px>
<br>Customer table creation using -t option with JSON format. The format is:
<br><b>{"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "extra": ["extra_option"], "items": ["column1", "column2", "column3"]}</b>
<ul>
<li>table_name: will be the database table name. Observe that this is the object main key.</li>
<li>quantity: number of items that will be downloaded and entered in the table (limited to 100 so far)</li>
<li>drop_if_exists: Default is true. will drop the table and create a new one if true. This will overwrite the --drop_if_exists option. By having this to no you can overcome the 100 items limitation (providing you keep the same columns throughout the runs)</li>
<li>id_increment: Default is true. will create an id field for the table and auto-increment it. This will overwrite the --id_increment option.</li>
<li>extra: Default is null. extra options. Useful for the product table only so far.</li>
<li>items: column names, as listed in the Fields section</li>
</ul>
<br>

<h3>Populating 1 table with colon-formatted option. Differently from the JSON-formatted -t option, all the fields must be present</h3>
<br><img src="readme_files/populate_1table_split.gif" width=700px>
<br>Customer table creation using -t option with colon format. The format is:
<b>table_name:quantity:drop_if_exists:id_increment:column1,column2,column3:extra</b>
<ul>
<li>table_name: will be the database table name. Observe that this is the object main key.</li>
<li>quantity: number of items that will be downloaded and entered in the table (limited to 100 so far)</li>
<li>drop_if_exists: will drop the table and create a new one if true. This will overwrite the --drop_if_exists option. By having this to no you can overcome the 100 items limitation (providing you keep the same columns throughout the runs)</li>
<li>id_increment: will create an id field for the table and auto-increment it. This will overwrite the --id_increment option.</li>
<li>items: column names, as listed in the Fields section. They must be separated by commas</li>
<li>extra: extra options. Useful for the product table only so far. Notice that in the colon formatted way, the extra option comes at the end</li>
</ul>

<h3>Populating 2 tables with JSON-formatted options</h3>
<br><img src="readme_files/populate_2tables_json.gif" width=700px>
<br>Product table is populated here. Notice that the extra option is informed with the content being a list with the string "product" and for items, no product name is indicated, as this is the default item for the table.

<h3>Populating 2 tables with colon-formatted options</h3>
<br><img src="readme_files/populate_2tables_split.gif" width=700px>
<br>Product table is populated here using the extra field. Differently from the JSON-formatted option, the extra field comes at the end, after the items. Similarly to the JSON-formatted option, the product name is not indicated, but is downloaded anyways.

<h3>Populating 4 related tables with JSON-formatted options</h3>
<br><img src="readme_files/populate_3tables_json.gif" width=1000px>
<br>This populates 4 tables that are related using JSON-formatted -t options. "customer", "sales_dept" and "products" are regular tables and sales is a transaction table, gluing all of the other tables together in one transaction (a sale per se).
Noitce that the only difference is that you need to provide as the "foreigner keys" the name of the foreigner table and its key in an object, all in the "items" item. In the database table, that column will be named foreigner_table__foreigner_key (separated by two underscore). Check below:<br>
<b>{"table_name": "quantity": 10, "drop_if_exists": true, "id_increment": true, "items": [{"foreigner_table": "foreigner_key"}, {"foreigner_table2": "foreigner_key"}, "column1", "column2", "column3"]}}</b>

<h3>Populating 3 related tables with colon-formatted options</h3>
<br><img src="readme_files/populate_3tables_split.gif" width=700px>
<br>This populates 3 related tables with colon-formatted -t options. in the items area, foreigner tables and their keys are indicated by having them as one item separated by __ (2 underscores). Check below:<br>
<b>table_name:quantity:drop_if_exists:id_increment:foreigner_table__foreigner_column, foreigner_table2__foreigner_column,column1,column2,column3</b>

<h3>Populating several tables using JSON file</h3>
<br><img src="readme_files/populate_several_tables_json.gif" width=700px>
<br>Instead of typing the tables in the command line, you can choose to have all of your configuration (including the database connection) in a JSON file. Use -i option to input that file and load the configuration. Check out the "input_files" folder that comes with 2 examples of such files, one with the database connection and one without it.


## Fields
<table>
<tr>
<th>Field</th><th>Field Description</th>
</tr>
<tr>
<td>name</td><td>field representing first name</td>
</tr>
<td>surname</td><td>field representing last name</td>
</tr>
<tr>
<td>email</td><td>field representing an email address</td>
</tr>
<tr>
<td>birthday</td><td>will populate field with date information</td>
</tr>
<tr>
<td>phone</td><td>field representing a phone number</td>
</tr>
<tr>
<td>company</td><td>will populate with company names</td>
</tr>
<tr>
<td>user_id</td><td>field representing a user identification</td>
</tr>
<tr>
<td>address</td><td>will populate with home/business address</td>
</tr>
<tr>
<td>city</td><td>will populate with city names (not in sync with region for country)</td></tr>
<tr>
<td>region</td><td>will populate with region names (State or Province) (not in sync with city or country)</td>
</tr>
<tr>
<td>country</td><td>will populate with country names (not in sync with city or region)</td>
</tr>
<tr>
<td>coordinates</td><td>will populate with latitude and longitude</td>
</tr>
<tr>
<td>cvisa</td><td>represents a visa card (credit)</td>
</tr>
<tr>
<td>cvisa_cvv</td><td>represents the visa card verification value</td>
</tr>
<tr>
<td>cmastercard</td><td>represents a mastercard card (credit)</td>
</tr>
<tr>
<td>cmastercard_cvv</td><td>represents the mastercard card verification value</td>
</tr>
<tr>
<td>username</td><td>will populate with usernames (first leter of name plus surname)</td>
</tr>
<tr>
<td>password</td><td>will populate with random password strings</td>
</tr>
<tr>
<td>salary</td><td>an amount that represents a salary</td>
</tr>
<tr>
<td>children</td><td>an integer representing the number of children of a person</td>
</tr>
<tr>
<td>price</td><td>an amount representing the price of a product</td>
</tr>
<tr>
<td>stock</td><td>an integer representing the product availability</td>
</tr>
<tr>
<td>contact</td><td>field representing someone's contact</td>
</tr>
<tr>
<td>quantity</td><td>an integer representing some quantity (amount of products sold, for exemple)</td>
</tr>
<tr>
<td>date</td><td>a date field (similar to birthday)</td>
</tr>
<tr>
<td>invoice</td><td>an integer representing an invoice number</td>
</tr>
<table>
