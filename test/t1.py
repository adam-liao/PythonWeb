import jieba

# text = "今天心情很低落，什麼都提不起勁"

while True:
    text = input("請輸入一段文字 (輸入 'exit' 或 'quit' 結束): ")
    if text.lower() == 'exit' or text.lower() == 'quit':
        break
    words = jieba.lcut(text)
    print(words)

print("程式已結束")