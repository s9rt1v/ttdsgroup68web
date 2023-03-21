#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:03:43 2023

@author: chennan
"""

from spellchecker import SpellChecker



def correction(query, file):
    '''
    # open the file in read mode
    with open(file, 'r') as f:
    # read all lines of the file into a list, and remove newline character from each line
        lines = [line.rstrip('\n') for line in f.readlines()]
    '''
    # create spell checker object
    spell = SpellChecker()
    
    # Add your proper nouns to the list of known words.
    spell.word_frequency.load_text_file(file)
    
    
    # split query into words
    words = query.split()

    # correct misspelled words
    corrected_words = []
    for word in words:
        corrected_words.append(spell.correction(word))
    print(corrected_words)
    if None in corrected_words:
        return []
    # join corrected words back into query
    corrected_query = " ".join(corrected_words)
        
    return corrected_query    



if __name__ == '__main__':
    non_en_list = correction('Black Panther: Wakanda Forever','non_en_words.txt')
    