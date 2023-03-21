#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:50:04 2023

@author: chennan
"""

import json
from collections import defaultdict

from nltk.corpus import wordnet


ordered_result = json.load(open("pii.txt"))
count=0

result=defaultdict(list)


for x in ordered_result.keys():
    synonyms=[]
    for syn in wordnet.synsets(x):
        for l in syn.lemmas():

            if (count < 3):
                if l.name().lower() not in synonyms and l.name().lower() in ordered_result.keys():
                    synonyms.append(l.name())
                    count += 1

    count=0

    for ele in synonyms:
        result[x].append(ele)

with open('synonyms.txt', 'w') as convert_file:
    convert_file.write(json.dumps(result))