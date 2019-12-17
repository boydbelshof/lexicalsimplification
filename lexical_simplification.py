#!/usr/bin/python3
#File: number_to_words.py
#By: Boyd Belshof, S3012158, Groep IK3
#This program takes an a number and translates it into natural language.
#Date: 24-11-15

import pickle, pyphen, operator, openpyxl
import pandas as pd
from operator import itemgetter
from stop_words import get_stop_words
from svm_wsd.dsc_wsd_tagger import parse_sentence
from cornetto.cornet import Cornet
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
   
# Load Cornetto Library
c = Cornet()
c.open("cornetto/cdb2.0.lu.stripped.xml", "cornetto/cdb2.0.syn.stripped.xml")

#Load Stopwords File
stop_words = get_stop_words('nl')

#Loads Pyphen Library
dic = pyphen.Pyphen(lang='nl_NL')

# Loads Dictionaries
with open('aoa.pickle', 'rb') as handle:
		aoa_dict = pickle.load(handle)

with open('wordcounter.pickle', 'rb') as handle:
		word_dict = pickle.load(handle)

with open('transformation.pickle', 'rb') as handle:
		transformation_dict = pickle.load(handle)

with open('troonrede_training_data.pickle', 'rb') as handle:
		training_dict = pickle.load(handle)

with open('../wordcounter_plain_python2.pickle', 'rb') as handle:
		word_freq_dict = pickle.load(handle)


data = pd.DataFrame(training_dict,columns=['aoa', 'count', 'len_', 'syl', 'syn', 'near_syn', 'hyper', 'hypo', 'label']) 
X = data[['aoa', 'count', 'len_', 'syl', 'syn', 'near_syn', 'hyper', 'hypo']]  # Features
y = data['label'] 
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X,y)

def is_stopword(word):
	if word in stop_words:
		return True
	else:
		return False

def create_pos_tags(tag):
	if tag in ['verbinf', 'verbpapa', 'verbpastpl', 'verbpastsg', 'verbpresp', 'verprespl', 'verbpressg', 'verb']:
		return 'verb'

	elif tag in ['noun*kop', 'nounabbr', 'nounpl', 'nounprop', 'noungsg', 'nounsg', 'prondemo', 'pronindef', 'pronposs', 'pronquest', 'pronrefl', 'pronrel']:
		return 'noun'

	elif tag in ['adj', 'adj*kop', 'adjabbr']:
		return 'adj'

	else:
		return None;

def get_aoa(word):
	if word in aoa_dict:
		return aoa_dict[word]
	else:
		return 0


def word_by_freq(word):
	return_synonym = word
	for synonym in synonyms:
		if return_synonym in word_dict and synonym in word_dict:
			if word_dict[return_synonym] < word_dict[synonym]:
				return_synonym = synonym
		elif return_synonym not in word_dict and synonym in word_dict:
			return_synonym = synonym

	return return_synonym


def get_related_words(x, method):
	# 0 = BY ID
	# 1 = BY TOKEN
	if method == 0:
		sense = c.get_lex_unit_by_id(x)
	else:
		sense = x
	related_items = c.get_related_lex_units(sense, '1')
	list_of_items = []
	if sense in related_items:
		if 'SYNONYM' in related_items[sense]:
			for item in related_items[sense]['SYNONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				list_of_items.append(item)
		if 'NEAR_SYNONYM' in related_items[sense]:
			for item in related_items[sense]['NEAR_SYNONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				list_of_items.append(item)
		if 'HAS_HYPONYM' in related_items[sense]:
			for item in related_items[sense]['HAS_HYPONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				list_of_items.append(item)
	return list_of_items

def get_right_form(lemma, tree_tagger_pos_tag):
	if lemma in transformation_dict:
		if tree_tagger_pos_tag in transformation_dict[lemma]:
			result = transformation_dict[lemma][tree_tagger_pos_tag]
			key = max(result.iteritems(), key=operator.itemgetter(1))[0]
			return key
	return lemma

def generate_key(lemma, pos_tag):
	if create_pos_tags(pos_tag) is not None:
		key = lemma + ":" + create_pos_tags(pos_tag) + ":1"
	else:
		key = lemma + ":1"
	return key

def keywithmaxval(d):
	highest_key = None
	for key in d:
		if highest_key is None:
			highest_key = key
		
		old = d[key][0][0]
		new = d[highest_key][0][0]
		if old > new:
			highest_key = key

	return highest_key, d[highest_key]

def should_simplify(word, lemma, pos_tag, key, _id, final_results):
	# PLAIN TEXT TODO
	list_of_synonyms = []

	if lemma in aoa_dict:
		aoa = (aoa_dict[lemma])

	count, list_of_synonyms = get_count_and_synonyms(_id, final_results, pos_tag, lemma, key)
	o_aoa = o_count = o_len_ = o_syl = o_syn = o_near_syn = o_hyper = o_hypo = 0
	if lemma in word_freq_dict:
		o_count = word_freq_dict[lemma]
	if lemma in aoa_dict:
		o_aoa = aoa_dict[lemma]
	o_syl = len(dic.inserted(lemma).split('-'))
	o_len_ = len(lemma)

	if _id in final_results:
		syn, near_syn, hyper, hypo = get_wordnet_features(final_results[_id][0], 0)
									
	# If not given create a WSD key
	else:
		new_tag = create_pos_tags(pos_tag)
		if new_tag is not None:
			key_list = c.get_lex_units(lemma + ":" + new_tag)
		else:
			key_list = c.get_lex_units(lemma)
			if len(key_list) > 0:
				key = key_list[0]
				o_syn, o_near_syn, o_hyper, o_hypo = get_wordnet_features(key, 1)			

	prediction = clf.predict([[o_aoa, o_count, o_len_, o_syl, o_syn, o_near_syn, o_hyper, o_hypo]])

	if prediction[0] == 1:
		return True
	else:
		return False


def get_wordnet_features(x, method):
	# 0 = BY ID
	# 1 = BY TOKEN
	if method == 0:
		sense = c.get_lex_unit_by_id(x)
	else:
		sense = x
	related_items = c.get_related_lex_units(sense, '1')
	syn = near_syn = hypo = hyper = 0
	if sense in related_items:
		if 'SYNONYM' in related_items[sense]:
			for item in related_items[sense]['SYNONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				syn += 1
		if 'NEAR_SYNONYM' in related_items[sense]:
			for item in related_items[sense]['NEAR_SYNONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				near_syn += 1
		if 'HAS_HYPERONYM' in related_items[sense]:
			for item in related_items[sense]['HAS_HYPERONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				hyper += 1
		if 'HAS_HYPONYM' in related_items[sense]:
			for item in related_items[sense]['HAS_HYPONYM']: # HIER KUNNEN ER NOG MEER ACHTER
				hypo += 1
	return syn, near_syn, hyper, hypo

def get_count_and_synonyms(_id, final_results, pos_tag, lemma, key):
	count = 0
	list_of_synonyms = []
	# Check if key is given by WSD
	if _id in final_results:
		list_of_synonyms = get_related_words(final_results[_id][0], 0)
		wordnet_features = len(list_of_synonyms)
		if key in word_dict:
			count = word_dict[key]
			
	# If not given create a WSD key
	else:
		new_tag = create_pos_tags(pos_tag)
		if new_tag is not None:
			key_list = c.get_lex_units(lemma + ":" + new_tag)
		else:
			key_list = c.get_lex_units(lemma)
			if len(key_list) > 0:
				key = key_list[0]
				list_of_synonyms = get_related_words(key, 1)
				if key in word_dict:
					count = word_dict[key]

	return count, list_of_synonyms

def get_simplification(word, lemma, pos_tag, key, _id, final_results):
	# PLAIN TEXT TODO
	list_of_synonyms = []

	if lemma in aoa_dict:
		aoa = (aoa_dict[lemma])

	count, list_of_synonyms = get_count_and_synonyms(_id, final_results, pos_tag, lemma, key)
	o_aoa = o_count = o_len_ = o_syl = o_syn = o_near_syn = o_hyper = o_hypo = 0
	if lemma in word_freq_dict:
		o_count = word_freq_dict[lemma]
	if lemma in aoa_dict:
		o_aoa = aoa_dict[lemma]
	o_syl = len(dic.inserted(lemma).split('-'))
	o_len_ = len(lemma)

	if _id in final_results:
		syn, near_syn, hyper, hypo = get_wordnet_features(final_results[_id][0], 0)
									
	# If not given create a WSD key
	else:
		new_tag = create_pos_tags(pos_tag)
		if new_tag is not None:
			key_list = c.get_lex_units(lemma + ":" + new_tag)
		else:
			key_list = c.get_lex_units(lemma)
			if len(key_list) > 0:
				key = key_list[0]
				o_syn, o_near_syn, o_hyper, o_hypo = get_wordnet_features(key, 1)			

	original = clf.predict_proba([[o_aoa, o_count, o_len_, o_syl, o_syn, o_near_syn, o_hyper, o_hypo]])

	if len(list_of_synonyms) > 0:
		synonyms = {}
		for synonym in list_of_synonyms:
			aoa = count = len_ = syl = syn = near_syn = hyper = hypo = 0
			synonym_lemma = synonym.split(':')[0]

			if synonym_lemma in word_freq_dict:
				count = word_freq_dict[synonym_lemma]
			if synonym_lemma in aoa_dict:
				aoa = aoa_dict[synonym_lemma]

			syllables_num = len(dic.inserted(synonym_lemma).split('-'))
			word_len = len(synonym_lemma)

			len_ = len(synonym_lemma)
			syl = len(dic.inserted(word).split('-'))

			new_tag = create_pos_tags(pos_tag)
			if new_tag is not None:
				key_list = c.get_lex_units(synonym_lemma + ":" + new_tag)
			else:
				key_list = c.get_lex_units(synonym_lemma)
				if len(key_list) > 0:
					key = key_list[0]
					syn, near_syn, hyper, hypo = get_wordnet_features(key, 1)	

			synonyms[synonym_lemma] = clf.predict_proba([[aoa, count, len_, syl, syn, near_syn, hyper, hypo]])
		
		syn_key, syn_val = keywithmaxval(synonyms)
		value = syn_val[0][0]

		if (original[0][0] < value):
			return syn_key, True
		else:
			return word, False
	return word, False

def simplify_sentence(sentence):
	tokens, final_results = parse_sentence(sentence)
	return_sentence = []
	for token in tokens:
		_id, word, pos_tag, lemma, number = token
		aoa = count = 0
		# Generate Key
		key = generate_key(lemma, pos_tag)
		old_word = word

		# Check for stopwords and pronouns
		if should_simplify(word, lemma, pos_tag, key, _id, final_results):
			word, new = get_simplification(word, lemma, pos_tag, key, _id, final_results)			
			if word is not None:
				if new is True:
					return_sentence.append(get_right_form(word, pos_tag))
				if new is False:
					return_sentence.append(old_word)
			else:
				return_sentence.append(old_word)	
		else:
			return_sentence.append(word)
	actual_sentence = ""
	for word in return_sentence:
		actual_sentence += word + ' '
	
	return actual_sentence

def main():
	while True:
		input_sentence = raw_input()
		print(simplify_sentence(input_sentence))

if __name__ == '__main__':
	main()

