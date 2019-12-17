from openpyxl import Workbook
import openpyxl
import string
import pickle
import pyphen
from stop_words import get_stop_words

#Load Stopwords File
stop_words = []

with open('stopwords.txt') as file:
	for word in file.readlines():
		stop_words.append(word.strip())

# print(stop_words)

new_workbook = openpyxl.load_workbook('annotated_bulte_test.xlsx')
sheet = new_workbook['Sheet']

counter = 0
not_bold_counter = 0

for col in sheet.iter_rows(min_col=1, max_col=51):
	sent = ""
	for cell in col:
		if cell.value is not None:
			if cell.font.bold is True:
				counter += 1
				sent += "**" + cell.value + "** "
			else:
				not_bold_counter += 1
				sent += cell.value + " "
	print(sent.strip().encode('utf-8'))



# print(counter)
# print(not_bold_counter)

	


