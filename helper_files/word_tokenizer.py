from nltk.tokenize import word_tokenize
import os
import string
import pickle
from operator import itemgetter
import treetaggerwrapper

tagger = treetaggerwrapper.TreeTagger(TAGLANG='nl')

table = str.maketrans(dict.fromkeys(string.punctuation)) 
word_dict = {}
filelist = os.listdir('Wikikids')
filelist2 = os.listdir('Wablieft/plain/')
total = len(filelist) + len(filelist2)
counter = 0
for x in filelist:
	counter += 1
	print(str(counter) + "/" + str(total))
	if x.endswith(".txt"):
		with open('Wikikids/' + x) as file:
			for line in file:
				return_line = ""
				tagged_line = tagger.tag_text(line)
				for item in tagged_line:
					splitted = item.split("\t")
					if len(splitted) > 2:
						lemma = splitted[2].lower()
						if lemma in word_dict:
							word_dict[lemma] += 1
						else:
							word_dict[lemma] = 1

for x in filelist2:
	counter += 1
	print(str(counter) + "/" + str(total))
	if x.endswith(".txt"):
		with open("Wablieft/plain/" + x) as file:
			for line in file:
				return_line = ""
				tagged_line = tagger.tag_text(line)
				for item in tagged_line:
					splitted = item.split("\t")
					if len(splitted) > 2:
						lemma = splitted[2].lower()
						if lemma in word_dict:
							word_dict[lemma] += 1
						else:
							word_dict[lemma] = 1


with open('wordcounter_plain_python2.pickle', 'wb') as handle:
    pickle.dump(word_dict, handle, protocol=2)
