import sys
import random
import re
import pymysql
import numpy as np
import os

def index(rank):
    if(rank <= 10):
        return 0
    elif(rank <= 20):
        return 1
    elif(rank <= 30):
        return 2
    elif(rank <= 50):
        return 3
    elif(rank <= 70):
        return 4
    elif(rank <= 100):
        return 5
    else:
        return -1

# I tried to use multiple class preceptron at first but it turn out to be useless
def learnData():
    
    # weight vectors
    top10 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    top20 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    top30 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    top50 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    top70 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    top100 = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    weights = [top10, top20, top30, top50, top70, top100]

    with open('secrete.json','r') as load_f:
        secrete = json.load(load_f)

    # 打开数据库连接
    db = pymysql.connect(secrete.s[0], secrete.s[1], secrete.s[2], secrete.s[3])

    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # 使用execute方法执行SQL语句
    cursor.execute("SELECT s.gpa, s.toefl, s.sat1, s.AP, s.recommadation, s.Vounteer, s.extra-activity, s.award, s.essay, c.rank From student s, college c WHERE s.collegeId = c.id")

    while True:
        curr_stu = cursor.fatchone()
        if curr_stu == None:
            break
        top_index = index(curr_stu[9])
        stu_info = []
        for i in range(9):
            stu_info.append(curr_stu[i])

        allZero = True
        for j in range(9):
            if weight[top_index][j] != 0:
                allZero = False
                break
        if allZero:
            for k in range(9):
                weights[top_index][k] = stu_info[k]
            continue

        dot_products = []
        max_index = 0
        max_dot = 0
        for i in range(len(weights)):
            curr_dot = np.dot(weights[i], stu_info)
            dot_products.append(curr_dot)
            if i == 0:
                max_dot = curr_dot    
            if curr_dot > max_dot:
                max_dot = curr_dot

        if top_index != max_index:
            weights[top_index] = map(lambda x, y: x + y, weights[top_index], stu_info)
            weights[max_index] = map(lambda x, y: x - y, weights[max_index], stu_info)



    # 关闭数据库连接
    db.close()
    
    # write the weights to json file
    path = 'weights.json'
    if os.path.exists(path): 
        os.remove(path) 
    fd = open(path, mode="w", encoding="utf-8")
    fd.close()

    load_dict = {
        'top10': weights[0],
        'top20': weights[1],
        'top30': weights[2],
        'top50': weights[3],
        'top70': weights[4],
        'top100': weights[5]
    }

    with open(path,"w") as dump_f:
        json.dump(load_dict,dump_f)


def predictRank(stu):

    with open('weights.json','r') as load_f:
        load_dict = json.load(load_f)

    top10 = load_dict['top10']
    top20 = load_dict['top20']
    top30 = load_dict['top30']
    top50 = load_dict['top50']
    top70 = load_dict['top70']
    top100 = load_dict['top100']

    weights = [top10, top20, top30, top50, top70, top100]
    w_class = ['top10', 'top20', 'top30', 'top50', 'top70', 'top100']
    max_index = 0
    max_dot = 0
    for i in range(len(weights)):
        curr_dot = np.dot(weights[i], stu_info)
        if i == 0:
            max_dot = curr_dot        
        if curr_dot > max_dot:
            max_dot = curr_dot
            max_index = i

    print("The predicted rank based on our database is : " + w_class[max_index])

def similar(gpa, toefl, sat):
    gpa_list = [2, 2.5, 2.75, 3, 3.2, 3.6, 3.8, 4]
    toefl_list = [60, 80, 90, 100]
    sat_list = [800, 1000, 1100, 1200, 1300, 1400, 1450, 1550]

    gpa_high, gpa_low = highlow(gpa, gpa_list)
    toefl_high, toefl_low = highlow(toefl, toefl_list)
    sat_high, sat_low = highlow(sat, sat_list)

    if(gpa_high == -1):
        gpa_high = sys.maxsize

    if(toefl_high == -1):
        toefl_high = sys.maxsize

    if(sat_high == -1):
        sat_high = sys.maxsize


    with open('secrete.json','r') as load_f:
        secrete = json.load(load_f)

    # 打开数据库连接
    db = pymysql.connect(secrete.s[0], secrete.s[1], secrete.s[2], secrete.s[3])
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()

    # 使用execute方法执行SQL语句
    cursor.execute("SELECT s.gpa, s.toefl, s.sat1, s.AP, s.recommadation, s.Vounteer, s.extra-activity, s.award, s.essay, c.rank From student s, college c WHERE s.collegeId = c.id")

    # 使用 fetchone() 方法获取一条数据
    data = cursor.fetchall()

    print "Database version : %s " % data

    count = [0,0,0,0,0,0,0]

    for curr_stu in data:

        if(gpa_low > gpa or gpa_high <= curr_stu[0]):
            continue
        if(toefl_low > gpa or toefl_high <= curr_stu[1]):
            continue
        if(sat_low > gpa or sat_high <= curr_stu[2]):
            continue
        print(curr_stu)
        if(curr_stu[9] <= 10):
            count[0] = count[0] + 1
        elif(curr_stu[9] <= 20):
            count[1] = count[1] + 1
        elif(curr_stu[9] <= 30):
            count[2] = count[2] + 1
        elif(curr_stu[9] <= 50):
            count[3] = count[3] + 1
        elif(curr_stu[9] <= 70):
            count[4] = count[4] + 1
        elif(curr_stu[9] <= 100):
            count[5] = count[5] + 1
        else:
            count[6] = count[6] + 1

    # 关闭数据库连接
    db.close()
    
    return true

def highlow(value, list):

    high = -1
    low = -1

    for curr in list:
        if(curr <= value):
            if(curr > low):
                low = curr
        if(curr > value):
            if(high == -1):
                high = curr
            else:
                if(curr < high):
                    high = curr

    return high, low
    
def predictRankNew():
    count = similar()
    count_total = 0
    for i in range(len(count)):
        count_total = count_total + count[i]
    top = ['top10', 'top20', 'top30', 'top50', 'top50', 'top70', 'top100', 'other']
    for j in range(len(top)):
        percentage = (count[j] / count_total) * 100
        print(top[j] + ' : ' + percentage + '%\n')


def main():

    gpa = input('input student gpa')
    toefl = input('input student toefl')
    sat1 = input('input sat1')
    AP = input('input AP')
    recommandation = input('input recommadation')
    volunteer = input('input volunteer')
    extra_acativity = input('input extra_activity')
    award = input('input award')
    essay = input('input essay')

    stu = [gpa, toefl, sat1, AP, recommadation, volunteer, extra_acativity, award, essay]

    wantSimilar = input('Do you want similar student infomation? Please input Y or y for yes and N or n for no.\n')
    while wantSimilar not in ['Y', 'y', 'N', 'n']:
        wantSimilar = input('Do you want similar student infomation? Please input Y or y for yes and N or n for no.\n')
    if wantSimilar in ['Y', 'y']:
        similar(gpa, toefl, sat1)

    wantPrediction = input('Do you want prediction? Please input Y or y for yes and N or n for no.\n')
    while wantPrediction not in ['Y', 'y', 'N', 'n']:
        wantPrediction = input('Do you want prediction? Please input Y or y for yes and N or n for no.\n')
    if wantPrediction in ['Y', 'y']:
        predictRankNew()        




if __name__ == "__main__":
    main()