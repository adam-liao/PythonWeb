# 導入 jieba 函式庫，用於中文斷詞
import jieba

# 原始程式碼中被註解掉的測試文字範例
# text = "今天心情很低落，什麼都提不起勁"

# 啟動一個無限迴圈，讓使用者可以重複輸入文字
while True:
    # 提示使用者輸入一段文字，並說明如何結束程式
    text = input("請輸入一段文字 (輸入 'exit' 或 'quit' 結束): ")

    # 檢查使用者輸入的文字，如果轉換成小寫後是 'exit' 或 'quit'
    if text.lower() == 'exit' or text.lower() == 'quit':
        # 則跳出迴圈，結束程式的輸入階段
        break

    # 使用 jieba.lcut() 函式對使用者輸入的文字進行精確模式斷詞
    # lcut() 會返回一個包含斷詞結果的列表 (list)
    words = jieba.lcut(text)

    # 輸出斷詞後的結果列表
    print(words)

# 當迴圈結束 (使用者輸入 'exit' 或 'quit') 時，印出程式結束的訊息
print("程式已結束")