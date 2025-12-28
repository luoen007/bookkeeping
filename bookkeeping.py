import json
import os
from datetime import datetime

USER_FILE = "users.json"
TYPE_FILE = "type.json"
DEFAULT_TYPES = {
    "支出":['购物','交通','餐饮','娱乐'],
    "收入":['工资','奖金','投资','兼职']
}

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path,'r',encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(file_path, users):
    with open(file_path,'w',encoding="utf-8") as f:
        json.dump(users,f,indent=4,ensure_ascii=False)

def init_types():
    if not os.path.exists(TYPE_FILE):
        save_data(USER_FILE, DEFAULT_TYPES)

class UserManager():
    def __init__(self):
        self.users = load_data(USER_FILE)
        if "admin" not in self.users:
            self.users["admin"] = {
                "password": "admin123",
                "is_admin": True,
                "records": [],
                "budget": 0,
                "remaining_budget": 0
            }
            save_data(USER_FILE, self.users)

    def register_user(self, username, password):
        if username in self.users:
            return False,"注册失败"
        self.users[username] = {
            "password": password,
            "is_admin": False,
            "records": [],
            "budget": 0,
            "remaining_budget": 0
        }
        save_data(USER_FILE, self.users)
        return True,"注册成功"

    def login(self, username, password):
        if username not in self.users:
            return False,"登录失败"
        if password not in self.users[username]["password"]:
            return False,"密码错误"
        return True,"登录成功",username

class Bookkeeping:
    def __init__(self,username):
        self.username = username
        self.users = load_data(USER_FILE)
        self.types = load_data(TYPE_FILE)

    def add_record(self,amount,type_,date,remark):
        record = {
            "amount": amount,
            "type": type_,
            "date": date,
            "remark": remark
        }
        self.users[self.username]["records"].append(record)
        if amount < 0:
            self.users[self.username]["remaining_budget"] += amount
        save_data(USER_FILE, self.users)
        return "记录添加成功"

    def get_record(self):
        return self.users[self.username]["records"]

    def update_record(self,index,new_data):
        records = self.users[self.username]["records"]
        if 0<=index<len(records):
            records[index].update(new_data)
            save_data(USER_FILE, self.users)
            return True,"修改成功"
        return False,"索引失败"

    def delete_record(self,index):
        records = self.users[self.username]["records"]
        if 0<=index<len(records):
            del records[index]
            save_data(USER_FILE, self.users)
            return True,"删除成功"
        return False,"删除失败"

class Statistics:

    def __init__(self,username):
        self.username = username
        self.users = load_data(USER_FILE)
        self.records = self.users[self.username]["records"]

    def total_balance(self):
        return sum([r["amount"] for r in self.records])

    def type_stat(self):
        stat_dict = {}
        for r in self.records:
            t=r["type"]
            stat_dict[t] = stat_dict.get(t,0) + r["amount"]
        return stat_dict

    def type_count(self):
        count_dict = {}
        for r in self.records:
            t=r["type"]
            count_dict[t] = count_dict.get(t,0) + 1
        return count_dict

class BudgetManager:
    def __init__(self,username):
        self.username = username
        self.users = load_data(USER_FILE)

    def set_budget(self,budget):
        self.users[self.username]["budget"] = budget
        save_data(USER_FILE, self.users)
        return "预算设置成功"

    def get_remaining_budget(self):
        return self.users[self.username]["remaining_budget"]

class AdminManager:
    def __init__(self):
        self.types = load_data(TYPE_FILE)

    def add_typ(self,category,type_name):
        if category in self.types and type_name not in self.types[category]:
            self.types[category].append(type_name)
            save_data(TYPE_FILE, self.types)
            return True, "类型添加成功"
        return False, "分类不存在或已存在"

    def delete_type(self,category,type_name):
        if category in self.types and type_name in self.types[category]:
            self.types[category].remove(type_name)
            save_data(TYPE_FILE, self.types)
            return True, "类型删除成功"
        return False, "类型不存在或分类不存在"

    def modify_user_pwd(self,username,new_pwd):
        users = load_data(USER_FILE)
        if username in users:
            users[username]["password"] = new_pwd
            save_data(USER_FILE, users)
            return True, "密码修改成功"
        return False,"用户不存在"


def main():
    init_types()
    user_manager = UserManager()
    current_user = None
    is_admin = False
    print("=====记账管理系统=====")
    while True:
        if not current_user:
            print("\n1.登录\n2.注册\n3.退出")
            choice = input("请选择操作：")
            if choice == "1":
                uname = input("用户名：")
                pwd = input("密码：")
                res,msg,*user = user_manager.login(uname, pwd)
                if res:
                    current_user = user[0]
                    is_admin = user_manager.users[current_user]["is_admin"]
                    print (msg)
                else:
                    print(msg)
            elif choice == "2":
                uname = input ("用户名：")
                pwd = input ("密码：")
                res,msg = user_manager.register(uname, pwd)
                print(msg)
            elif choice == "3":
                print ("退出系统")
                break
            else:
                print ("操作无效，请重新输入")
        else:
            print(f"\n===== 欢迎{current_user} =====\n")
            if is_admin:
                print("1.记账管理\n2.统计查询\n3.预算管理\n4.管理员功能\n5.退出登录")
            else:
                print("1.记账管理\n2.统计查询\n3.预算管理\n4.退出登录")
            choice = input ("请选择:")
            if choice == "1":
                book = Bookkeeping(current_user)
                print("1.添加记录\n2.查询记录\n3.修改记录\n4.删除记录")
                sub_choice = input ("请选择:")
                if sub_choice == "1":
                    amount = float(input ("金额(收入正/支出负):"))
                    print("可选类型",load_data(TYPE_FILE))
                    t = input("类型：")
                    date = input ("日期(默认格式YYYY-MM-DD):")or datetime.now().strftime("%Y-%m-%d")
                    remark = input ("备注：")
                    print(book.add_record(amount,t,date,remark))
                elif sub_choice == "2":
                    records = book.get_record()
                    if records:
                        for i, r in enumerate(records):
                            print(f"{i},{r}")
                    else :
                        print("暂无记录")
                elif sub_choice == "3":
                    idx = int (input ("要修改的记录索引："))
                    new_data = {}
                    if input ("是否修改金额(y/n):") == 'y':
                        new_data["amount"] = float(input("新金额："))
                    if input ("是否修改类型(y/n):") == 'y':
                        new_data["type"] = input("新类型：")
                    if input ("是否修改日期(y/n):") == 'y':
                        new_data["date"] = input("新日期：")
                    if input ("是否修改备注(y/n):") == 'y':
                        new_data["remark"] = input("新备注：")
                    res,msg = book.update_record(idx,new_data)
                    print(msg)
                elif sub_choice == "4":
                    idx = int (input ("要删除的记录索引："))
                    res,msg = book.delete_record(idx)
                    print(msg)
            elif choice == "2":
                stat = Statistics(current_user)
                print(f"总金额：{stat.total_balance()}")
                print("按类型统计收支：",stat.type_stat())
                print("消费类型次数：",stat.type_count())
            elif choice == "3":
                budget = BudgetManager(current_user)
                print("\n1. 设置本月预算\n2.查看剩余预算")
                sub_choice = input("请选择：")
                if sub_choice == "1":
                    b = float(input("请输入本月预算："))
                    print(budget.set_budget(b))
                elif sub_choice == "2":
                    print(f"本月预算剩余：{budget.get_remaining_budget()}")
            elif choice == "4" and is_admin:
                admin = AdminManager()
                print("\n1.管理消费类型\n2.修改用户密码")
                sub_choice = input("请选择：")
                if sub_choice == "1":
                    print("\n1.添加类型\n2.删除类型")
                    s = input ("请选择：")
                    if s == "1":
                        cate = input ("分类(收入/支出):")
                        t_name = input ("类型名称：")
                        res,msg = admin.modify_user_pwd(cate,t_name)
                        print(msg)
                    elif s == "2":
                        cate = input("分类(收入/支出):")
                        t_name = input("类型名称：")
                        res, msg = admin.delete_type(cate, t_name)
                        print(msg)
                elif sub_choice == "2":
                    uname = input ("要修改的用户名：")
                    new_pwd = input("新密码：")
                    res,msg = admin.modify_user_pwd(uname,new_pwd)
                    print(msg)
            elif choice == "5" and is_admin or choice == "4" and not is_admin:
                current_user = None
                is_admin = False
                print("退出登录成功")
            else:
                print("输入无效，请重新选择")


if __name__ == "__main__":
    main()