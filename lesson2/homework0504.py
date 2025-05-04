
import random as rnd

student= []

def readfile():
    with open('./names.txt', 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()
            if name:
                student.append(name)

readfile()

# 隨機選 3 個學生
result = rnd.sample(student, 3)
print("🎲 隨機抽出的名字：")
for i in result:
    print(i)


# name.txt的內容
# 陳怡伶
# 馮芳如
# 蒙淑惠
# 張軒宸
# 陳向愛
# 賴心怡
# 王怡珊
# 林詠斌
# 陳淑娟
# 崔孝憲