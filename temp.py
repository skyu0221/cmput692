import csv, json
import numpy as np
from pprint import pprint
import difflib
import numeral
from tqdm import tqdm
import Levenshtein
import itertools

NUMBERS = "0123456789"
DELIMITERS = "~!@#$%^&*()_+`-={}|[]\:<>?;',./'" + '"'
ROMAN = "IVXL"

CATEGORY_RATIO = 0.3
CATEGORY_NUMBER = 5

FREQUENCY_RATIO = 0.1
FREQUENCY_NUMBER = 1

DISTANCE_THRESHOLD = 1
SIMILARITY_THRESHOLD = 0.9

little_result_counter = 0


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


def judge_categorical(unique, count, table):
    global little_result_counter

    count_freq = count / sum(count)
    # candidates = unique[np.logical_or(count <= FREQUENCY_NUMBER, count_freq <= FREQUENCY_RATIO)]

    for pairs in itertools.combinations(unique, 2):
        if pairs[0] == pairs[1]:
            continue

        jaro_score = Levenshtein.jaro(pairs[0], pairs[1])
        l_ratio = Levenshtein.ratio(pairs[0], pairs[1])
        score = jaro_score * l_ratio

        if score >= SIMILARITY_THRESHOLD:

            word_0 = pairs[0].split(' ')
            word_1 = pairs[1].split(' ')

            score = 0
            for a in word_0:
                for b in word_1:
                    if a != b:
                        jaro_score = Levenshtein.jaro(a, b)
                        l_ratio = Levenshtein.ratio(a, b)
                        word_score = jaro_score * l_ratio

                        score = max(score, word_score)

        # blocks = difflib.SequenceMatcher(None, pairs[0], pairs[1]).get_matching_blocks()
        # diff_0 = list()
        # diff_1 = list()
        # prefix = pairs[0][:blocks[0].a]
        # if len(prefix) != 0:
        #     diff_0.append(prefix)
        # prefix = pairs[1][:blocks[0].b]
        # if len(prefix) != 0:
        #     diff_1.append(prefix)
        #
        # for i in range(1, len(blocks)):
        #     if blocks[i - 1].a + blocks[i - 1].size != blocks[i].a:
        #         diff_0 += [pairs[0][blocks[i - 1].a + blocks[i - 1].size:blocks[i].a]]
        #     if blocks[i - 1].b + blocks[i - 1].size != blocks[i].b:
        #         diff_1 += [pairs[1][blocks[i - 1].b + blocks[i - 1].size:blocks[i].b]]
        #
        # diff = list(set(diff_0)) + list(set(diff_1))
        #
        # diff_lower = [x.lower() for x in diff]
        #
        # possibility = 1
        #
        # for i in range(len(diff)):
        #
        #     roman = True
        #     for char in diff[i]:
        #         if char not in ROMAN:
        #             roman = False
        #             break
        #
        #     if diff[i].lower() in diff_lower[] or diff[i] in DELIMITERS:
        #         possibility = 1
        #         break
        #
        #     if roman:
        #         possibility *= 0.5
        #     else:
        #         possibility *= 0.9



        # diff_0 = []
        # diff_1 = []
        # chars_0 = sorted(list(pairs[0]))
        # chars_1 = sorted(list(pairs[1]))
        #
        # while len(chars_0) != 0 and len(chars_1) != 0:
        #     if chars_0[0] == chars_1[0]:
        #         chars_0.pop(0)
        #         chars_1.pop(0)
        #     elif chars_0[0] > chars_1[0]:
        #         diff_1.append(chars_1.pop(0))
        #     else:
        #         diff_0.append(chars_0.pop(0))
        # final_score = jaro_score * l_ratio * possibility

        if score >= SIMILARITY_THRESHOLD:
            # if min(len(candidate), len(compare)) <= 2:
            #     continue
            # if len(candidate) > len(compare):
            #     diff = set(candidate) - set(compare)
            # else:
            #     diff = set(compare) - set(candidate)
            # for char in list(diff):
            #     if char in DELIMITERS:
            #         print("Candidates:", candidate, "and", compare)
            #         print("Unique, count:", unique, count)
            #         print("=================")
            print(table)
            print("Candidates:", pairs[0], "and", pairs[1])
            print("Unique, count:", unique, count)
            print("Similarity:", score)
            print("=================")
            # input()
            little_result_counter += 1


def extract_data():
    global little_result_counter

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
            if any(char in NUMBERS + DELIMITERS for char in data):
                numerical = True
                break

        if not numerical:
            counter += 1
            judge_categorical(unique_entry, unique_count, table)

        # if not numerical and (ratio < CATEGORY_RATIO or unique_entry.shape[0] < CATEGORY_NUMBER):
        #     counter += 1
        #     judge_categorical(unique_entry, unique_count)
    print(counter)
    print("Found:", little_result_counter)


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