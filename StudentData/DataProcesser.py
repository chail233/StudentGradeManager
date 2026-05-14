import pandas as pd
import re
import time
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