import json
import math
from nltk.stem import PorterStemmer

from nltk.stem import snowball

from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
import numpy as np
from xml.dom import minidom


snowball = SnowballStemmer(language="english")

def Phrase(query,data, data1):
            # wordloc_list stores the document and the inner location each word appears (list)
            ordered_result = data

            wordloc_list = defaultdict(list)
            wordloc_list=ordered_result
            # print(wordloc_list['panther'])
            indexQuery1 = 1
            query=query.lower()
            split = query.split(' ')

            strs = split
            arr=[]
            dicter = dict()

            # variable switch is to imply whether a phrase exists in this query
            switch = 0
            # variable implier is to imply whether two phrases appear in this query
            implier=0
            # first and second word of the phrase
            fir = ""
            sec = ""

            occur=[]
            for i, s in enumerate(strs):
                if '"' in s:
                    occur.append(i)

            for ele in strs:

                # handle the phrase search case
                if (ele[0] == '''"''' and implier == 0):
                    switch = 1
                    implier = 1
                    # arr = []
                    ele2 = ele

                    fir = ele.replace('''"''', "")
                    fir = snowball.stem(fir)

                    if (len(strs) == 1):
                        for ele in wordloc_list[fir]:
                            jump=list((ele.keys()))[0]
                            arr.append(int(jump))
                        return arr
                    else:
                        sec = strs[strs.index(ele2) + occur[1]-occur[0]].replace('''"''', "")
                        sec = snowball.stem(sec)
                        if(fir in ordered_result.keys() and sec in ordered_result.keys()):
                            for ele3 in wordloc_list[fir]:
                                for ele4 in wordloc_list[sec]:
                                    ele31=list(ele3.values())[0][0]
                                    ele41=list(ele4.values())[0][0]
                                    # use proximity distance == 1 to decide if it is a phrase
                                    if (list(ele3.keys())[0] == list(ele4.keys())[0] and int(ele41) - int(ele31)==occur[1]-occur[0]  and list(ele3.keys())[0] not in arr):
                                        dicter[int(list(ele3.keys())[0])]=data1.loc[data1['id'] == int((list(ele3.keys())[0])), 'vote_average'].iloc[0]

                        dicter=dict(sorted(dicter.items(), key=lambda item: item[1]))
                        return dicter.keys()

                # handle the proximity search case
                if (ele[0] == '#'):
                    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~+`=|'''
                    for ele1 in ele:
                        if ele1 in punc:
                            strs[0] = strs[0].replace(ele1, " ")
                    strs1 = strs[0].split()

                    # proximity number
                    dis = int(strs1[0])
                    fir = snowball.stem(strs1[1])
                    sec = strs[1]
                    for ele1 in sec:
                            if ele1 in punc:
                                sec = sec.replace(ele1, "")
                    sec = snowball.stem(sec)

                    if (fir in ordered_result.keys() and sec in ordered_result.keys()):
                        for ele3 in wordloc_list[fir]:
                            for ele4 in wordloc_list[sec]:
                                ele31 = list(ele3.values())[0][0]
                                ele41 = list(ele4.values())[0][0]
                                # use proximity distance == 1 to decide if it is a phrase
                                if (list(ele3.keys())[0] == list(ele4.keys())[0] and int(ele41) - int(ele31) < dis and int(ele41)-int(ele31)>0
                                         and list(ele3.keys())[0] not in arr):
                                    dicter[int(list(ele3.keys())[0])]=data1.loc[data1['id'] == int((list(ele3.keys())[0])), 'vote_average'].iloc[0]

                    dicter = dict(sorted(dicter.items(), key=lambda item: item[1]))
                    return dicter.keys()
