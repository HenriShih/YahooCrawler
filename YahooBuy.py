__author__ = 'Henri_Shih'

__version__ = '2.0.0'

import requests
from lxml import etree
import time
import sys
import json
import csv
import xlwt

"""
Description :
This is a cmd interface web crawler for fetching best sale items on yahoo platform

Prerequisite :
Simply run pip install -r requirements.txt to install all required libraries
1. requests
2. lxml
3. xlwt

User Story:
1. Run this script in command line interface and select operation function :
   - python Yahoo.py --cat or python --item
2. Fetch all category information from portal page into category_list json and csv files.
   - python Yahoo.py --cat
3. Read category_list_options file, remove unwanted categories lines and save the file.
   - after modifying category_option file, run 'python Yahoo.py --item' again.
   - check selected options from prompt message and proceed the program if everything is all right.
4. Fetch best sale items of selected categories and choose output type (csv, excel or both) from prompt input.
   - after fetching output data, select output report formats from prompt input (1.csv, 2.excel, 3.both)
5. Output results to csv or xslt files

Functions:
1. main():
2. fetch_cat_list():
3. fetch_best_item_list(cat_idx_list):
4. table_generator(num):
5. generate_output(output_data, file_option):

Files:
1. category_list.json : Category information db for program to search.
2. category_list_options.csv : Configuration file for user to select their category preference.
3. output_csv.csv : Final report of best sale items in csv format.
4. output_xsl.xls : Final report of best sale items in xls format.

Important configurations:
1. ITEM_NUMS : Define how many best sale items will crawler fetch for each category

Command line arguments:
--cat  : fetch_cat_list
--item : fetch_best_item_list 

Limitation:
1. This crawler only fetch best 5 of total sales items in the categories with catiditem number,
   other types of categories and best sale items might not be covered.
2. Some categories does not have best sale items in the page will return empty list.
3. It will take approximate 3 seconds to fetch 10 best sale items for one category,
   thus, it will take more than 1 hour if you fetch for more than 1200 categories.
4. Some best sale products might have special price rather than listing price.

"""

# Configurations of the crawler
PORTAL_URL = 'https://tw.buy.yahoo.com'
SUFFIX = '&sort=-tsales&pg=1'
ITEM_NUMS = 10


class YahooCrawler:
    def __init__(self, num=ITEM_NUMS, url=PORTAL_URL, suffix=SUFFIX):
        self.item_num = num
        self.url = url
        self.suffix = suffix

    def fetch_cat_list(self):
        req = requests.get(self.url).text
        page_content = req.replace('<!--', " ")  # Cleaning comment tags to get hidden info
        page_content2 = page_content.replace('-->', " ")
        page_tree = etree.HTML(page_content2)
        cat_urls_pre = page_tree.xpath('//div[@class="catLevel3 yui3-u"]/a/@href')
        cat_names_pre = page_tree.xpath('//div[@class="catLevel3 yui3-u"]/a/text()')
        cat_all_pre = list(zip(cat_names_pre, cat_urls_pre))
        # Cleaning and transforming non catitemid data, then building the dictionary and list for json and csv output
        cat_urls = []
        cat_names = []
        cat_all_dict = {}
        cat_all_list = [['CatId', 'CatName']]
        for cat_pre in cat_all_pre:
            cat_id = cat_pre[1].split('?')[1]
            cat_name = cat_pre[0]
            if cat_id.startswith('catitemid'):
                print('It is a catitem category...')
                cat_url = self.url + '/?' + cat_id + self.suffix
                cat_idx = cat_id.split('=')[1]
                cat_urls.append(cat_url)
                cat_names.append(cat_name)
                cat_all_dict[cat_idx] = [cat_name, cat_url]
                cat_all_list.append([cat_idx, cat_name])
            elif cat_id.startswith('catid'):  # Catid categories need to go to sub_page to fetch catitemid info
                print('Oops!, It is a catid category, and we need further processing...')
                sub_page_url = self.url + '/?' + cat_id
                sub_req = requests.get(sub_page_url)
                sub_content = sub_req.text
                sub_tree = etree.HTML(sub_content)
                sub_urls = sub_tree.xpath('//div[@id="cl-catproduct"]/div/h2/span/a/@href')
                sub_names = sub_tree.xpath('//div[@id="cl-catproduct"]/div/h2/span/a/text()')
                sub_all = list(zip(sub_names, sub_urls))
                for sub in sub_all:
                    print('Adding cat_url and cat_name in the subpage to the list...')
                    name = sub[0]
                    url = sub[1]
                    idx = url.split('=')[1]
                    sub_url = self.url + url + self.suffix
                    cat_urls.append(sub_url)
                    cat_names.append(name)
                    cat_all_dict[idx] = [name, sub_url]
                    cat_all_list.append([idx, name])
            else:  # Other irrelevant items shall be obsoleted
                print('Oh no, it is an irrelevant item, we will abandon it...')
        with open('category_list_options.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(cat_all_list)
        cat_all_json = json.dumps(cat_all_dict, ensure_ascii=False)
        print(cat_all_json, file=open('category_list.json', 'w', encoding='utf-8'))
        return cat_all_dict, cat_all_json

    def fetch_best_items(self,cat_ids):
        try:
            open('category_list.json', 'r', encoding='utf-8')
        except FileNotFoundError:
            print('Cannot find category_list file, fetching category_list now...')
            self.fetch_cat_list()
        try:
            open('category_list_options.csv', 'r',encoding='utf-8')
        except FileNotFoundError:
            print('Cannot find category_option file, fetching category_list now...')
            self.fetch_cat_list()
        with open('category_list.json', 'r', encoding='utf-8') as f:
            cat_dict = json.load(fp=f)
        # Build request category dictionary and output_table
        request_cat_dict = {}
        output_table = self.table_generator(self.item_num)
        for x in cat_ids:
            key = str(x)
            val = cat_dict[key]
            request_cat_dict[key] = val
        # Fetch best sale products for each request category
        for y in request_cat_dict.keys():
            cat_name = request_cat_dict[y][0]
            prod_url = request_cat_dict[y][1]
            prod_page = requests.get(prod_url).text
            prod_tree = etree.HTML(prod_page)
            prod_name = prod_tree.xpath('//div[@class="srp-pdtitle"]/a/@title')
            prod_price = prod_tree.xpath('//div[@class="srp-listprice"]/span[2]/text()')
            prod_all = list(zip(prod_name, prod_price))
            best_10 = prod_all[:self.item_num]
            request_cat_dict[y].append(best_10)
            output_list = [y, cat_name]
            for z in best_10:
                output_list.append(z[0])
                output_list.append(z[1])
            output_table.append(output_list)
        # Generate output file with output_table and input option
        print('Data is ready, please select your output option...')
        option = int(input('1. csv , 2. excel , 3. both '))
        self.generate_output(output_table, option)
        return output_table

    def generate_output(self,output_data, file_option):  # 1 = csv, 2 = xls, 3 = both
        if file_option == 1:
            print('System is preparing your file in csv format...')
            with open('output_csv.csv', 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(output_data)
            print('File is ready, Have a nice day!')
        elif file_option == 2:
            print('System is preparing your file in csv format...')
            book = xlwt.Workbook(encoding='utf-8')
            sheet1 = book.add_sheet('Best10')
            for i in range(len(output_data)):
                for j in range(len(output_data[i])):
                    sheet1.write(i, j, output_data[i][j])
            book.save('output_xsl.xls')
            print('File is ready, Have a nice day!')
        elif file_option == 3:
            print('System is preparing your file in both csv and xls formats...')
            with open('output_csv.csv', 'w', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(output_data)
            book = xlwt.Workbook(encoding='utf-8')
            sheet1 = book.add_sheet('Best%d' % self.item_num)
            for i in range(len(output_data)):
                for j in range(len(output_data[i])):
                    sheet1.write(i, j, output_data[i][j])
            book.save('output_xsl.xls')
            print('Files are ready, Have a nice day!')
        else:
            print('System cannot recognize your option, printing in console...')
            print(output_data)

    def table_generator(self,num):
        table = [['Cat_Id', 'Cat_Name']]
        for t in range(int(num)):
            new_num = str(t + 1)
            rank_name = 'No%s_Name' % new_num
            rank_price = 'No%s_Price' % new_num
            table[0].extend([rank_name, rank_price])
        return table


def main():
    app = YahooCrawler()
    action = str(sys.argv[1])
    if action == '--cat':
        print('You want to get category list, please wait...')
        app.fetch_cat_list()
    elif action == '--item':
        """
        try:
            _select_categories[0]
        except IndexError:
            print('You have not input catids option...')
        """
        try:
            open('category_list_options.csv', 'r',encoding='utf-8')
        except FileNotFoundError:
            print('Cannot find category_option file, fetching category_list now...')
            app.fetch_cat_list()
            print('Category_list fetched... please modify the category_list_option.csv file with your preference...')
            sys.exit(1)
        options_cat = []
        options_name = []
        with open('category_list_options.csv', 'r',encoding='utf-8', newline='\n') as fo:
            options_all = csv.reader(fo)
            for row in options_all:
                if row[0] == 'CatId':
                    pass
                else:
                    options_cat.append(row[0])
                    options_name.append(row[1])
        print('You want to fetch best sale items of below categories, please wait...')
        for name in options_name:
            print(name)
        proceed = input('Are you sure to fetch items for above categories( Y / N ) ?')
        if proceed == 'Y' or proceed == 'y':
            print('Fetching best items, please wait...')
            app.fetch_best_items(options_cat)
        else:
            print('Process terminated...please try again later...')
            sys.exit(1)
    else:
        print('We cannot recognize your action, please try again...')


if __name__ == '__main__':
    start = time.time()
    main()
    elapsed_time = time.time() - start
    print('Total elapsed time = %s seconds...' % str(elapsed_time))