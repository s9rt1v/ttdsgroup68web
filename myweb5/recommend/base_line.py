#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 15:39:56 2023

@author: chennan
"""

import pandas as pd
import string
import collections
import re
import math
from nltk.stem import PorterStemmer
import os


import json



# Tokenization and Case folding
class Preprocessing:
    def __init__(self, data):
        # Text data
        self.data = data

    def get_preprocessing_result(self):
        exclist = string.punctuation
        table_ = str.maketrans(exclist, ' '*len(exclist))
        text_no_pun = ' '.join(self.data.translate(table_).split())
        token_lower = text_no_pun.lower().split()
        # Stop-word data
        with open(os.getcwd() + "/recommend/englishST.txt", 'r', encoding='utf-8-sig') as f:
            lines = [line.rstrip() for line in f]
        # Stopping
        s = set(lines)
        result = [x for x in token_lower if x not in s]
        #  Normalisation
        ps = PorterStemmer()
        stemming_words = []
        for w in result:
            stemming_words.append(ps.stem(w))
        return stemming_words

class Positional_Inverted_Index:
    def __init__(self, data):
        self.data = data
        
    def get_pii_no_df(self):
        self.matrix = []
        self.doc_ids = []
        for i, t, g, o in zip(data['id'], data['title'], data['genres'], data['overview']):
            
            self.doc_ids.append(i)
            total_string = t + g + o
            p = Preprocessing(total_string)
            tokens = p.get_preprocessing_result()
            self.matrix.append(tokens)
        
    
                
        self.result = {}

        for doc_id, doc in zip(self.doc_ids, self.matrix):
            for word in set(doc):
                inside_dic = {}
                inside_dic.setdefault(doc_id, [])
                inside_dic[doc_id] = [word_position + 1 for word_position, w in enumerate(doc) if w == word]
                self.result.setdefault(word, []).append(inside_dic)

        self.ordered_result = collections.OrderedDict(sorted(self.result.items()))
        return self.ordered_result
    
    def get_pii(self): # use get_pii_no_df first 
        self.positional_inverted_index = {}
        for k in self.ordered_result:
            self.positional_inverted_index[(k,len(self.ordered_result[k]))] = self.ordered_result[k]
        return self.positional_inverted_index

    def tf_idf(self,tokens, ordered_result): 
        # N , ordered_result to database
        #N = len(self.doc_ids)
        N = 340684
        doc_position = []
        for t in tokens:
            doc_position.append(ordered_result[t])
        list_list_w =[]    
        for t in doc_position:
            df = len(t)
            idf = math.log10(N/df)
            w_list= []
            for d in t:
                tf = len(list(d.values())[0])
                w  = (1 + math.log10(tf)) * idf
                w_list.append((int(list(d.keys())[0]),w))
            list_list_w.append(w_list)
            
        flattened = [val for sublist in list_list_w for val in sublist] 
        # Converting it to a dictionary
        tup = {i:0 for i, v in flattened}
        for key, value in flattened:
            tup[key] = tup[key]+value
        # using map
        result = list(map(tuple, tup.items()))
        result.sort(key=lambda x:x[1], reverse=True)
        return result[:20]       
    
    def bm25(self, tokens, ordered_result, term_count):
        N  = 340684
        l_avg = 26.628412252996913
        doc_position = []
        for t in tokens:
            doc_position.append(ordered_result[t])
        list_list_w =[] 
        for t in doc_position:
            df = len(t)
            w_list= []
            for d in t:
                tf = len(list(d.values())[0])
                l_d = term_count[list(d.keys())[0]]
                w = (tf/(1.5*(l_d/l_avg)+tf+0.5))*math.log10((N-df+0.5)/(df+0.5))
                w_list.append((int(list(d.keys())[0]),w))
            list_list_w.append(w_list)
        flattened = [val for sublist in list_list_w for val in sublist] 
        # Converting it to a dictionary
        tup = {i:0 for i, v in flattened}
        for key, value in flattened:
            tup[key] = tup[key]+value
        # using map
        result = list(map(tuple, tup.items()))
        result.sort(key=lambda x:x[1], reverse=True)
        return result[:20]     
    
    def index_file(self):
        
        with open('index.txt', 'w') as f:
            for k in self.positional_inverted_index.keys():
                s = k[0]+":"+str(k[1])
                f.write(s)
                f.write('\n')

                for d in self.positional_inverted_index[k]:
                    docID = str(list(d.keys())[0])
                    f.write("\t"+docID+": ")
                    pos_s = []
                    for p in list(d.values())[0]:
                        pos = str(p) + ","
                        pos_s.append(pos)
                    pos_string = ' '.join(pos_s)
                    pos_string = pos_string[:-1]
                    f.write(pos_string)
                    f.write('\n')  
      
    def rank_scores_tf_idf(self,query, ordered_result):   
        prep_data = []
        p = Preprocessing(query).get_preprocessing_result()
        prep_data.append(p)
        self.results_rank = []    
        for x in prep_data:
            self.results_rank.append(self.tf_idf(x, ordered_result))
        return self.results_rank 
    
    def rank_scores_bm25(self,query, ordered_result, term_count):   
        prep_data = []
        p = Preprocessing(query).get_preprocessing_result()
        prep_data.append(p)
        self.results_rank = []    
        for x in prep_data:
            self.results_rank.append(self.bm25(x, ordered_result, term_count))
        return self.results_rank

data = pd.read_csv(os.getcwd() + '/recommend/movies_clean.csv')
data.fillna('', inplace=True)
p = Positional_Inverted_Index(data)
ordered_result = json.load(open(os.getcwd() + "/recommend/pii.txt"))
#term_count = json.load(open(os.getcwd() + "/recommend/term_count.txt"))
def mainSearch(query):
    p.rank_scores_tf_idf(query, ordered_result)

    #p.rank_scores_bm25('Black Panther: Wakanda Forever', ordered_result, term_count)
    
