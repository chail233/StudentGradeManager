from StudentData import DataProcesser
path = "data/scores.csv"
Running = True
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
    def __init__(self):
        self.studata = DataProcesser.StuData(path)

    def run(self):
        self.show_info()

    #展示菜单信息
    def show_info(self):
        for s in self.info:
            print(s)
        self.transit()
    #获取选项
    @staticmethod
    def get_choice(a, b):
        while True:
            sopt = input()
            if not sopt:
                continue
            try:
                opt = int(sopt)
            except ValueError:
                print("输入有误请重新输入:")
                continue
            if a<=opt<=b:
                return opt
            else:
                print("输入有误，请重新输入！")

    #转入功能
    def transit(self):
        opt = self.get_choice(1,8)
        if opt == 1:
            self.add_score()
        elif opt == 2:
            self.query()
        elif opt == 3:
            self.modify()
        elif opt == 4:
            self.delele()
        elif opt == 5:
            pass
        elif opt == 6:
            pass
        elif opt == 7:
            pass
        else:
            self.exit_program()

    def add_score(self):
        self.studata.add_score()

    def query(self):
        print("1.按学号查询")
        print("2.列出所有")
        print("请选择：")
        opt = self.get_choice(1, 2)
        self.studata.query(opt)

    def modify(self):
        self.studata.modify()

    def exit_program(self):
        self.studata.save_df()
        print("数据已保存!")
        print("退出")
        global Running
        Running = False

    def delele(self):
        print("1.按学号删除所有成绩")
        print("2.按学号+科目删除单科成绩")
        opt = self.get_choice(1, 2)
        if opt == 1:
            print("请输入学号：")
            sid = input()
            self.studata.delete_all(sid)
        else:
            print("请输入学号 科目：")
            sid, subject = input()
            self.studata.delete_subject(sid, subject)
if __name__ == "__main__":

    menu = Menu()
    while Running:
        menu.run()