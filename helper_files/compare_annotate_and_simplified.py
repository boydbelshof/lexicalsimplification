with open('test_annotated_testset.txt') as annotated:
	annotated_lines = annotated.readlines()

with open('test_rf_testset.txt') as rf:	
	rf_lines = rf.readlines()

counter = 0

for (line, line_1) in zip(annotated_lines, rf_lines):
	for (word, word_1) in zip(line.split(" "), line_1.split(" ")):
		word = word.strip().lower()
		word_1 = word_1.strip().lower()

		if word[:2] == "**":
			if word_1[:2] != "**" and word_1[:2] != "^^":
					counter += 1
					print(counter)