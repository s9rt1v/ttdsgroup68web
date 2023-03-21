#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 16:25:45 2023

@author: chennan
"""

import pandas as pd
import string
import collections

import json
from nltk.stem import PorterStemmer

def cleanning(data):
     
    df = pd.read_csv(data)
    df_en = df.loc[df['original_language'] == 'en']
    '''
    df_en.duplicated().sum()
    df_en['title'].duplicated().sum()
    
    df_en.drop_duplicates(inplace=True)
    '''
    df_en = df_en[df_en['status']=='Released']
    
    df_en.drop_duplicates(subset=['title','release_date'], inplace=True)
        
    
    df_en = df_en.drop(columns=['production_companies', 'budget', 'revenue', 'status', 'tagline', 'original_language'])
    
    '''
    df_en.isnull().sum()
    '''
    
    df_en.fillna('', inplace=True)
    
    index = df_en[(df_en['genres']=='') & (df_en['overview']=='')].index
    
    
    df_en['release_date'] = pd.to_datetime(df_en['release_date'], format='%Y-%m-%d')
    
    df_en.drop(index, inplace=True)
    
    df_en = df_en.dropna(subset=['title', 'poster_path', 'backdrop_path'])
    
    
    return df_en


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
        with open("englishST.txt", 'r', encoding='utf-8-sig') as f:
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
        self.term_count = []
        for i, t, g, o in zip(data['id'], data['title'], data['genres'], data['overview']):
            
            self.doc_ids.append(i)
            weighted_t = " ".join([t]*50)
            total_string = " ".join([weighted_t, g, o])
            #print(total_string)
            p = Preprocessing(total_string)
            tokens = p.get_preprocessing_result()
            self.term_count.append(len(tokens))
            self.matrix.append(tokens)
        
        def Average(lst):
            return sum(lst) / len(lst)
        
        self.term_count_avg = Average(self.term_count)
                
        self.result = {}

        for doc_id, doc in zip(self.doc_ids, self.matrix):
            for word in set(doc):
                inside_dic = {}
                inside_dic.setdefault(doc_id, [])
                inside_dic[doc_id] = [word_position + 1 for word_position, w in enumerate(doc) if w == word]
                self.result.setdefault(word, []).append(inside_dic)

        self.ordered_result = collections.OrderedDict(sorted(self.result.items()))
        return self.ordered_result
    
    def pii_to_txt(self):
        with open('pii.txt', 'w') as convert_file:
            convert_file.write(json.dumps(self.ordered_result))
    
    def term_count_to_txt(self):
        dictionary = dict(zip(self.doc_ids, self.term_count))
        with open('term_count.txt', 'w') as convert_file:
            convert_file.write(json.dumps(dictionary))           
            
if __name__ == '__main__':
    data = cleanning('movies.csv.zip')
    data.to_csv('movies_clean.csv', encoding='utf-8',date_format ='%Y-%m-%d',index=False)
    
    
    
    p = Positional_Inverted_Index(data)
    p.get_pii_no_df()
    #N to database
    N = len(p.doc_ids)
    print(N)
    #26.628412252996913
    p.term_count_to_txt()
    print(p.term_count_avg)
    p.pii_to_txt()
    