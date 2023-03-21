import pandas as pd
import enchant
import re

d = enchant.Dict("en_US")
df = pd.read_csv('movies_clean.csv', encoding='utf8')
df['title']= df['title'].astype('string')
df = df.dropna(subset=['title','poster_path', 'backdrop_path'])

def filter_non_english_words(text):
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    non_english_words = []
    for word in words:
        if not d.check(word):
            non_english_words.append(word)
    return non_english_words

# apply function to text column
df['non_english_words'] = df['title'].apply(filter_non_english_words)

res = df['non_english_words'].values.tolist()

res_no_empty = [ele for ele in res if ele !=[]]
flat_list = [item for sublist in res_no_empty for item in sublist]

with open('non_en_words.txt', 'w', encoding="utf-8") as f:
    for item in flat_list:
        f.write("%s\n" % item)