#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:39:50 2023

@author: chennan
"""


import json

import nltk
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.corpus import wordnet
import os


def expansion(query):

    query_o=query;
    query=query.split()
    synonyms = []

    count = 0
    ordered_result = json.load(open(os.getcwd() + "/recommend/synonyms.txt"))

    for x in query:
            for syn in wordnet.synsets(x):
                    for l in syn.lemmas():
                        if (count < 3):
                            if l.name().lower() not in synonyms and l.name().lower() in ordered_result.keys():
                                synonyms.append(l.name())
                                count += 1

            count = 0

    for ele in synonyms:
            if ele in query_o.split() :
                synonyms.remove(ele)

    synonyms_string = ' '.join(synonyms)
    new_query = " ".join([query_o,synonyms_string])


    return new_query



