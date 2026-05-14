import pandas as pd
import re
import time
import matplotlib.pyplot as plt
from numpy.ma.extras import average


#带暂停的输出
def tprint(s):
    print(s)
    time.sleep(1)
class StuData:
    subjects = ["语文", "数学", "英语"]
    pattern_id = r'^\d{8}$'
    pattern_score = r'^(\d{1,2}|100)$'
    def __init__(self, path):
        #初始化数据
        self.path = path
        self.df_scores = pd.read_csv(self.path, header=None, names=['id', 'name', '语文', '数学', '英语'],
                                     dtype={'id': str, 'name': str, '语文':str, '数学':str, '英语':str})
        self.df_scores.set_index('id', inplace=True)
        print("成功加载数据:")
        print(self.df_scores)

    #获取df
    def get_df(self):
        return self.df_scores
    # 保存df到csv
    def save_df(self):
        self.df_scores.to_csv(self.path, header=False)

    #成绩格式校验
    def check(self, sid, subject, score, name):
        if not re.fullmatch(self.pattern_id, sid):
            return False
        if not re.fullmatch(self.pattern_score, score):
            return False
        if subject not in self.subjects:
            return False
        if sid not in self.df_scores.index:
            self.df_scores.loc[sid] = [name, pd.NA, pd.NA, pd.NA]
            return True
        if pd.isna(self.df_scores.loc[sid, subject]):
            return True
        else:
            return False

    #添加成绩
    def add_score(self):
        print("输入：学号、姓名、科目（语文/数学/英语）、成绩")
        pid,pname,psubject,pscore = input().split()
        if self.check(pid, psubject, pscore, pname):
            self.df_scores.loc[pid, psubject] = pscore
            self.save_df()
            tprint(f"添加成功！\n {self.df_scores.loc[pid]}")
        else:
            tprint("数据格式有误或重复添加！")

    #格式化输出信息
    def print_student(self, sid):
        data = self.df_scores.loc[sid]
        infos = [sid, data['name'], str(data['语文']), str(data['数学']), str(data['英语'])]
        print(" ".join(infos))

    #查询成绩
    def query(self, opt):
        if opt == 1:
            print("请输入学号：")
            sid = input()
            if self.check_sid(sid):
                self.print_student(sid)
        else:
            print(" ".join(["id", "name", "语文", "数学", "英语"]))
            for row in self.df_scores.itertuples():
                self.print_student(str(row.Index))
        tprint("")

    #校验学号
    def check_sid(self, sid):
        if not re.fullmatch(self.pattern_id, sid):
            tprint("学号格式错误！")
            return False
        if sid not in self.df_scores.index:
            tprint("该学号不存在！")
            return False
        return True
    #修改成绩
    def modify(self):
        print("请输入：学号 科目 分数")
        sid, subject, score = input().split()
        if not self.check_sid(sid):
            return
        if subject not in self.subjects:
            tprint("科目不存在！")
            return
        if not re.fullmatch(self.pattern_score, score):
            tprint("分数格式错误！")
            return
        self.df_scores.loc[sid, subject] = score
        self.save_df()
        tprint("修改成功！")

    #删除成绩
    def delete_all(self, sid):
        if self.check_sid(sid):
            self.df_scores.loc[sid, "语文"] = pd.NA
            self.df_scores.loc[sid, "数学"] = pd.NA
            self.df_scores.loc[sid, "英语"] = pd.NA
            self.save_df()
            tprint("删除成功！")
    def delete_subject(self, sid, subject):
        if self.check_sid(sid):
            if subject not in self.subjects:
                tprint("该科目不存在！")
                return
            self.df_scores.loc[sid, subject] = pd.NA
            self.save_df()
            tprint("删除成功！")

    #数据清洗
    def clean(self):
        self.save_df()
        #处理空值
        self.df_scores.dropna(inplace=True)
        #去除异常id值
        for row in self.df_scores.itertuples():
            if not re.fullmatch(self.pattern_id, row.Index):
                self.df_scores.drop(row.Index, inplace=True)
        #删除重复学生
        rid = []
        for row in self.df_scores.itertuples():
            if row.Index in rid:
                self.df_scores.drop(row.Index, inplace=True)
            else:
                rid.append(row.Index)
        #处理异常分数
        for row in self.df_scores.itertuples():
            if not re.fullmatch(self.pattern_score, row.语文):
                self.df_scores.loc[row.Index, "语文"] = 0
            if not re.fullmatch(self.pattern_score, row.数学):
                self.df_scores.loc[row.Index, "数学"] = 0
            if not re.fullmatch(self.pattern_score, row.英语):
                self.df_scores.loc[row.Index, "英语"] = 0
        #处理名字文本
        for row in self.df_scores.itertuples():
            self.df_scores.loc[row.Index, "name"]=self.df_scores.loc[row.Index, "name"].strip()
            self.df_scores.loc[row.Index, "name"]=self.df_scores.loc[row.Index, "name"].lower()
        #保存
        self.df_scores.to_csv("data/scores_clean.csv", header=False)
        tprint("清洗完成！")


    #数据可视化
    def plot_average(self):
        categories = ['语文', '数学', '英语']
        values = [average(list(map(int, self.df_scores['语文']))), average(list(map(int, self.df_scores['数学']))), average(list(map(int, self.df_scores['英语'])))]
        plt.bar(categories, values)
        plt.show()