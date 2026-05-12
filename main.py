import pandas as pd

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

    df_scores = pd.read_csv("/data/scores.csv", header=None, names=['id', 'name', 'chinese', 'math', 'english'])

    #展示菜单信息
    def show_info(self):
        for s in self.info:
            print(s)
    #成绩格式校验
    def check(self):
        pass
    #添加成绩
    def add_score(self):
        print("输入：学号、姓名、科目（语文/数学/英语）、成绩")
        pid,pname,psubject,pscore = input().split()
        pscore = int(pscore)
        if self.check():
            pass
        else:
            print("数据格式有误！")

if __name__ == "__main__":
    menu = Menu()
    while True:
        menu.show_info()