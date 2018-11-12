## Yahoo Buy  Best Sale Items Crawler
This is a Python script which you can simply execute it to fetch best sale items from buy.yahoo.com platform

## Prerequisite
Simply run pip install -r requirements.txt to install all required libraries
1. requests
2. lxml
3. xlwt

## Use Case
1. Run this script in command line interface and select operation function :
   - python Yahoo.py --cat or python --item
2. Fetch all category information from portal page into category_list json and csv files.
   - python Yahoo.py --cat
   - **Suggest to run this function once a while to keep the category_list up-to-date**  
3. Read category_list_options file, remove unwanted categories lines and save the file.
   - after modifying category_option file, run 'python Yahoo.py --item' again.
   - check selected options from prompt message and proceed the program if everything is all right.
4. Fetch best sale items of selected categories and choose output type (csv, excel or both) from prompt input.
   - after fetching output data, select output report formats from prompt input (1.csv, 2.excel, 3.both)
5. Output results to csv or xslt files

## Generated Files:
1. category_list.json : Category information db for program to search.
2. category_list_options.csv : Configuration file for user to select their category preference.
3. output_csv.csv : Final report of best sale items in csv format.
4. output_xsl.xls : Final report of best sale items in xls format.

## Important configurations:
1.  ITEM_NUMS : Define how many best sale items will crawler fetch for each category

## Limitation:
1. This crawler only fetch best 5 of total sales items in the categories with catiditem number,
   other types of categories and best sale items might not be covered.
2. Some categories does not have best sale items in the page will return empty list.
3. It will take approximate 3 seconds to fetch 10 best sale items for one category,
   thus, it will take more than 1 hour if you fetch for more than 1200 categories.
4. Some best sale products might have special price rather than listing price.
