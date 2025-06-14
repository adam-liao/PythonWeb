import jieba

text = "今天心情很低落，什麼都提不起勁"
words = jieba.lcut(text)
print(words)