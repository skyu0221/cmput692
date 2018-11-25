import csv, json
import numpy as np
from pprint import pprint
from tqdm import tqdm
from Levenshtein import distance

CATEGORY_RATIO = 0.3
CATEGORY_NUMBER = 5

FREQUENCY_RATIO = 0.1
FREQUENCY_NUMBER = 1

DISTANCE_THRESHOLD = 1


class Table:

    def __init__(self):
        # url, section, column, caption, value
        self.url = None
        self.caption = None
        self.section = None
        self.column_index = None
        self.header = None
        self.value = None

    def set_values(self, data_row):
        self.set_url(data_row[0])
        self.set_caption(data_row[1])
        self.set_section(data_row[2])
        self.set_column_index(data_row[3])
        self.set_header(data_row[4])
        self.add_value(data_row[5].split("___"))
        self.value_to_np()

    def set_url(self, url):
        if len(url) != 0:
            self.url = url

    def set_caption(self, caption):
        if len(caption) != 0:
            self.caption = caption

    def set_section(self, section):
        if len(section) != 0:
            self.section = section

    def set_column_index(self, column_index):
        self.column_index = column_index

    def set_header(self, header):
        if len(header) != 0:
            self.header = header

    def add_value(self, data):
        if len(data) != 0:
            if self.value is None:
                if type(data) == list:
                    self.value = data
                else:
                    self.value = [data]
            else:
                if type(data) == list:
                    self.value += data
                else:
                    self.value.append(data)

    def value_to_np(self):
        self.value = np.asarray(self.value, dtype=str)

    def write_to_file(self, csvwriter):
        values = "___".join(list(self.value))
        data_row = [self.url, self.caption, self.section, self.column_index, self.header, values]
        csvwriter.writerow(data_row)

    def __str__(self):
        string = ""
        string += "Wiki URL:      " + str(self.url) + '\n'
        string += "Table Caption: " + str(self.caption) + '\n'
        string += "Wiki Section:  " + str(self.section) + '\n'
        string += "Column #:      " + str(self.column_index) + '\n'
        string += "Header:        " + str(self.header) + '\n'
        string += "Values:        " + str(self.value)
        return string


def judge_categorical(unique, count):

    count_freq = count / sum(count)
    candidates = unique[np.logical_or(count <= FREQUENCY_NUMBER, count_freq <= FREQUENCY_RATIO)]

    for candidate in candidates:
        for compare in unique:
            if candidate != compare:
                if distance(candidate, compare) <= DISTANCE_THRESHOLD:
                    if min(len(candidate), len(compare)) <= 2:
                        continue
                    if len(candidate) > len(compare):
                        diff = set(candidate) - set(compare)
                    else:
                        diff = set(compare) - set(candidate)
                    for char in list(diff):
                        if char in "~!@#$%^&*()_+`-={}|[]\:<>?;',./'" + '"':
                            print("Candidates:", candidate, "and", compare)
                            print("Unique, count:", unique, count)
                            print("=================")



def extract_data():
    database = []
    with open("wiki_input.tsv", 'r', encoding="utf8") as input_file:
        reader = csv.reader(input_file, delimiter='\t')
        counter = 0
        for row in reader:
            table = Table()
            table.set_values(row)
            database.append(table)
            counter += 1

    print(counter)
    counter = 0

    for table in database:
        total_size = table.value.shape[0]
        unique_entry, unique_count = np.unique(table.value, return_counts=True)
        unique_size = unique_entry.shape[0]
        ratio = unique_size / total_size

        numerical = False
        for data in unique_entry:
            if any(char.isdigit() for char in data):
                numerical = True
                break

        if not numerical and (ratio < CATEGORY_RATIO or unique_entry.shape[0] < CATEGORY_NUMBER):
            counter += 1
            judge_categorical(unique_entry, unique_count)
    print(counter)


def load_json():
    with open("tables.json", 'r', encoding="utf8") as input_file:
        with open("database.tsv", 'w+', encoding="utf8", newline='') as output_file:
            writer = csv.writer(output_file, delimiter='\t')

            for line in tqdm(input_file):
                dictionary = json.loads(line)
                all_column = []
                for column in range(dictionary["numCols"]):
                    table_col = Table()
                    table_col.set_column_index(column)
                    if "tableCaption" in dictionary.keys():
                        table_col.set_caption(dictionary["tableCaption"])
                    if "sectionTitle" in dictionary.keys():
                        table_col.set_section(dictionary["sectionTitle"])
                    table_col.set_header(dictionary["tableHeaders"][0][column]["text"])
                    all_column.append(table_col)

                for row in dictionary["tableData"]:
                    for column in range(dictionary["numCols"]):
                        all_column[column].add_value([row[column]["text"]])

                for column in all_column:
                    unique = np.unique(column.value)
                    if unique.shape[0] == 1 and unique[0] in (None, ''):
                        continue
                    column.write_to_file(writer)


def extract_auto_detect_data():
    with open("wiki_pooling_Auto-Detect.tsv", 'r', encoding="utf8") as input_file:
        reader = csv.reader(input_file, delimiter='\t')
        for row in reader:
            if row[-1] != '1':
                print(Table())
                print(row[-2].split("___"), row[-1])
                print("============")


if __name__ == '__main__':
    extract_data()
