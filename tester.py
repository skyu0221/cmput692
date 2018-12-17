import random

DELIMITERS = "~!@#$%^&*()_+`={}|[]:<>?;',./'\\" + '"'
NUMBERS = "0123456789"

RANDOM_NUM = 20


def switch(list_name):
    if list_name[-1]:
        list_name.append('')


random_element = list(map(str, range(1, RANDOM_NUM + 1)))
for _ in range(RANDOM_NUM):
    random_word = ''
    for _ in range(random.randint(1, 10)):
        random_word += chr(random.randint(ord('A'), ord('Z')))
    random_element.append(random_word)
random.shuffle(random_element)

print(random_element)
print(len(random_element))

random_string = "#$%^&"
for element in random_element:
    random_string += element + random.randint(1, 3) * random.choice(DELIMITERS)
print(random_string)

numerical_result = ['']
categorical_result = ['']

for ch in random_string:
    if ch not in DELIMITERS:
        if ch not in NUMBERS:
            categorical_result[-1] += ch
            switch(numerical_result)
        else:
            numerical_result[-1] += ch
            switch(categorical_result)
    else:
        switch(numerical_result)
        switch(categorical_result)

if not numerical_result[-1]:
    numerical_result.pop()
if not categorical_result[-1]:
    categorical_result.pop()

print(len(numerical_result))
print(numerical_result)
print(len(categorical_result))
print(categorical_result)
