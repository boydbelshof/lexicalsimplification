from openpyxl import Workbook


book = Workbook()
sheet = book.active

with open("bulte_testset.txt") as file:
	for i, line in enumerate(file.readlines()):
		for j, word in enumerate(line.split(" ")):
			sheet.cell(row=i+1, column=j+1).value = word


book.save("bulte_test.xlsx")
