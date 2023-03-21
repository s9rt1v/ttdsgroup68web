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
from spellchecker import SpellChecker

from . import Phrase
from .query_correction import *
from .query_expansion import *
import simplejson as json
import os
from .models import *



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
        result = result[:20]
        return [x[0] for x in result]      
    
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
        result = result[:10000]
        return  [x[0] for x in result]
    
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
    
    def get_detail(self, l, data):
        res = data.iloc[pd.Index(data['id']).get_indexer(l)]
        return res
            
    def rank_scores_tf_idf(self,query, ordered_result):   
        p = Preprocessing(query).get_preprocessing_result()
        
        return self.tf_idf(p, ordered_result)
    
    def rank_scores_bm25(self,query, ordered_result, term_count):   
        p = Preprocessing(query).get_preprocessing_result()
        
        return self.bm25(p, ordered_result, term_count)


data = pd.read_csv(os.getcwd() + '/recommend/movies_clean.csv', encoding='utf8')
data.fillna('', inplace=True)
p = Positional_Inverted_Index(data)
ordered_result = json.load(open(os.getcwd() + "/recommend/pii.txt"))
term_count = json.load(open(os.getcwd() + "/recommend/term_count.txt"))

def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele+" "

    # return string
    return str1

def mainSearch(query):

    movies = []
    phrase = False
    for i in query.split():
        if (i[0] in '''"'''):
                phrase = False;
                query = listToString(re.findall(r'"([^"]*)"', query))
                break
        if (i[0] in '''#'''):
            phrase = True
            a=p.get_detail(Phrase.Phrase(query, ordered_result, data), data)

            for i in range(len(a.index)):
                movies.append(
                    Movie_new(a.index[i], a['id'].iloc[i], a['title'].iloc[i], a['genres'].iloc[i],
                              a['overview'].iloc[i],
                              a['popularity'].iloc[i], a['release_date'].iloc[i], a['runtime'].iloc[i],
                              a['vote_average'].iloc[i],
                              a['vote_count'].iloc[i], a['credits'].iloc[i], a['keywords'].iloc[i],
                              a['poster_path'].iloc[i],
                              a['backdrop_path'].iloc[i], a['recommendations'].iloc[i]))
            return movies
            break
    if (phrase == False):



        corrected_query = correction(query, os.getcwd() + '/recommend/non_en_words.txt')
        if corrected_query == []:
            return "No result"
        # print(corrected_query)
        #expaned_query = expansion(corrected_query)
        # print(expaned_query)
        # res_bm25 = p.rank_scores_bm25('Black Panther: Wakanda Forever', ordered_result, term_count)
        #res_tfidf = p.rank_scores_tf_idf(corrected_query, ordered_result)
        res_bm25 = p.rank_scores_bm25(corrected_query, ordered_result, term_count)
        a = p.get_detail(res_bm25, data)
        #res_tfidf_expanse = p.rank_scores_bm25(expaned_query, ordered_result,term_count)
        for i in range(len(a.index)):
            movies.append(
                Movie_new(a.index[i], a['id'].iloc[i], a['title'].iloc[i], a['genres'].iloc[i], a['overview'].iloc[i],
                          a['popularity'].iloc[i], a['release_date'].iloc[i], a['runtime'].iloc[i],
                          a['vote_average'].iloc[i],
                          a['vote_count'].iloc[i], a['credits'].iloc[i], a['keywords'].iloc[i], a['poster_path'].iloc[i],
                          a['backdrop_path'].iloc[i], a['recommendations'].iloc[i]))

        return movies
