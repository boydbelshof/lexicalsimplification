# Thesis Information Science: Dutch Lexical Simplification

Python2.7 program for simplifying Dutch sentences on lexical level. This program was part of a research of adding features to existing lexical simplification systems. 


## Data Files
For this research several data resources were used, these are available upon request (B.J.Belshof@student.rug.nl). These datafiles are Cornetto (only with a valid license), Dutch Wikipedia, Wikikids.

## Packages
This program uses several packages which have to be installed before running, these are:
```
pickle
pyphen
operator
openpyxl
pandas
stop_words
sklearn
```

SVM_WSD[https://github.com/cltl/svm_wsd]
PYCornetto[https://github.com/emsrc/pycornetto]

## Usage
Program takes a sentence as input and outputs the simplified sentence. As an example:
```bash
echo "Onze samenleving wordt steeds diverser, maar dat blijkt niet uit de vriendschappen die jongeren sluiten." | python lexical_simplification.py
```
