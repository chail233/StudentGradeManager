import pandas as pd
import re
import os

class Menu(object):
    info = ["==== 学生成绩管理与分析系统 ====",
            "1. 添加学生成绩",
            "2. 查询学生成绩（单个/全部）",
            "3. 修改学生成绩",
            "4. 删除学生成绩",
            "5. 数据清洗与格式化",
            "6. 成绩统计分析",
            "7. 成绩可视化图表",
            "8. 退出系统",
            "=============================",
            "请输入功能编号："
            ]

    df_scores = pd.read_csv("data/scores.csv", header=None, names=['id', 'name', '语文', '数学', '英语'])

    def __init__(self):
        self.df_scores.set_index('id', inplace=True)

    #展示菜单信息
    def show_info(self):
        for s in self.info:
            print(s)
        self.transit()
    #获取选项
    def get_choice(self):
        while True:
            sopt = input()
            if not sopt:
                continue
            opt = int(sopt)
            if 1<=opt<=8:
                return opt
            else:
                print("输入有误，请重新输入！")
    #转入功能
    def transit(self):
        opt = self.get_choice()
        if opt == 1:
            self.add_score()
    #成绩格式校验
    def check(self, id, subject, score, name):
        pattern_id = r'^\d{8}$'
        if not re.fullmatch(pattern_id, id):
            return False
        pattern_score = r'^(\d{1,2}|100)$'
        if not re.fullmatch(pattern_score, score):
            return False
        if id not in self.df_scores.index:
            self.df_scores.loc[id] = [name, pd.NA, pd.NA, pd.NA]
            return True
        if pd.isna(self.df_scores.loc[id, subject]):
            return True
        else:
            return False


    #添加成绩
    def add_score(self):
        print("输入：学号、姓名、科目（语文/数学/英语）、成绩")
        pid,pname,psubject,pscore = input().split()
        if self.check(pid, psubject, pscore, pname):
            self.df_scores.loc[pid, psubject] = pscore
            self.df_scores.to_csv("data/scores.csv")
            print(f"添加成功！{self.df_scores.loc[pid]}")
        else:
            print("数据格式有误或重复添加！")

if __name__ == "__main__":

    menu = Menu()
    while True:
        menu.show_info()