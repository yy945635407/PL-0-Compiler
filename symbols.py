class STable:
    #符号表类
    def __init__(self):
        self.table = []  # 存放表项
        self.outer = None
        #self.dx = 0 #表项偏移

    def MakeTable(self,outer):
        self.outer = outer

    def Enter(self,name,kind,level=0,adr=0,val=0,form=False):
        #向符号表增加项
        symbol = Symbol()
        symbol.set(name,kind,level,adr,val,form)
        self.table.append(symbol)
       #self.dx += 1

    def GetSymbol(self,s):
        #找到符号表中的定义
        t = self
        while t != None:#由内层向外层查找
            for tr in t.table:
                if s == tr.name:
                    return tr
            t = t.outer
        return None

    def GetFormalId(self):
        #返回当前函数的形参
        FormalId = []
        if self.outer == None:
            return FormalId
        procSym = self.outer.table[-1] #外层表的最新符号项就是该过程的说明
        paramNum =procSym.val #参数值
        for i in range(1,paramNum+1):
            FormalId.append(self.outer.table[-1-i].name)
        FormalId.append(procSym.name) #返回列表中最后一个元素存过程名
        return FormalId

    def GetLast(self):
        return self.table[-1]

    def GetExtraFormalParamNum(self):#返回本表中多余的形参所占存储空间个数
        num = 0
        for item in self.table:
            if item.kind == "procedure":
                num += item.val
        return num

    def show(self):#打印当前符号表的表项
        for item in self.table:
            print(item)

    def showall(self):#打印所有符号表链上的表项
        t = self
        while t != None:
            for item in t.table:
                print(item)
            t = t.outer


class Symbol:
    def __init__(self):
        # 符号表项
        self.name = ""  # 名称
        self.kind = ""  # 类型
        self.val = 0  # 值(常量值和过程的参数个数)
        self.level = 0  # 嵌套层次
        self.adr = 0  # 活动记录中相对地址
        self.form = False # 记录该变量是否是形参,用于验证变量是否被定义
        self.maxnum = 10000000

    def set(self,name,kind,level,adr,val,form):
        self.name = name
        self.kind = kind
        if kind == "const":
            if val<self.maxnum:
                self.val = val
            else:
                print("The value of"+name+"is too large!")
        elif kind == "var":
            self.level = level
            self.adr = adr
            self.form = form
        elif kind == "procedure":
            self.level = level
            self.val = val
            self.adr = adr

    def __str__(self):
        if self.kind == "const":
            str = "name:{0:<5}\tkind:{1:<5}\tval:{2:<5}"
            return str.format(self.name, self.kind, self.val)
        elif self.kind == "var":
            str = "name:{0:<5}\tkind:{1:<5}\tval:{2:<5}\tlevel:{3:<5}\tadr:{4:<5}"
            return str.format(self.name, self.kind, self.val, self.level, self.adr)
        else:
            str = "name:{0:<5}\tkind:{1:<5}\tlevel:{2:<5}\tval:{3:<5}"
            return str.format(self.name, self.kind, self.level, self.val)
