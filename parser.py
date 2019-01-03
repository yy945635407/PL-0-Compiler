import difflib
import lexical
from symbols import *
from Pcodes import *
class lexicalimpl:
    #词法分析器实现类
    def __init__(self):
        self.i = 0  # 词法单元索引
        self.lines = []
        self.lex = lexical.lexical()
        # 分别记录前一个，当前，下一个词法单元
        self.previous = ""
        self.current = ""
        self.next = ""
        # f = open("result.txt")
        # self.lines = f.readlines()
        # f.close()
        self.current = self.lex.analyse()
        self.next = self.lex.analyse()

    def sym(self):#取词
        # if self.i == len(self.lines):
        #     return False
        # return self.lines[self.i].split('.')[0]
        if self.current != None:
            return self.current.split('.')[0]
        else:
            return False

    def gettype(self):#得到类别
        # return self.lines[self.i].split('.')[1]
        return self.current.split('.')[1]

    def getline(self):#得到行号
        # return self.lines[self.i].split('.')[2]
         return self.current.split('.')[2]

    def getpreline(self):#得到前一个行号
        # if self.i<len(self.lines) and self.getline() == "1\n":
        #     return "1\n"
        # return self.lines[self.i-1].split('.')[2]
        if self.previous == "":
            return "1\n"
        else:
            return self.previous.split('.')[2]

    def advance(self):
        self.i += 1
        self.previous = self.current
        self.current = self.next
        if self.next != None:
            self.next = self.lex.analyse()

class parser:
    #语法分析器
    def __init__(self):
        self.topTable = None #最内层符号表
        self.procs = [] # 描述函数的参数个数和语句起始位置,其中单元为[函数名，参数个数，语句起始位置]
        self.Codes = PcodeTable() #代码区（表）
        self.level = 0 #嵌套层次
        self.iserror = 0 #记录是否有错
        self.dx = 0 #变量在活动记录中的相对地址
        self.lex = lexicalimpl()
        self.first = {"prog": ["program"], "block": ["const", "var", "procedure", "begin"], "condecl": ["const"],
                 "vardecl": ["var"], "proc": ["procedure"]
            , "body": ["begin"], "statement": ["if", "while", "call", "begin", "read", "write"],
                 "lexp": ["odd", "(", "+", "-"],
                 "exp": ["+", "-", "("],
                 "term": ["("], "factor": ["("], "lop": ["=", "<>", "<", ">=", ">", "<="], "aop": ["+", "-"],
                 "mop": ["*", "/"],
                 "id": [], "integer": [], "const": []}
        # note:
        # first["const"]=first["id"],first["statement"]=first["id"]+first["body"]+"if"+"while"...
        # first["lexp"]=first["exp"]+"odd",first["exp"]=first["term"]+ "+" + "-",first["term"]=first["factor"]
        # first["factor"]=first["id"]+first["integer"]+"(",
        # then:
        # first["const"] = first["id"], first["statement"] = first["id"] + "begin" + "if" + "while"...
        # first["lexp"]=first["id"]+first["integer"]+"("+ "+" + "-"+"odd",
        # first["exp"]=first["id"]+first["integer"]+"("+ "+" + "-",
        # first["term"]=first["id"]+first["integer"]+"("
        # first["factor"]=first["id"]+first["integer"]+"(",
        # if self.gettype=="标识符",self.sym is in first["id"];
        # if self.gettype=="常数",self.sym is in first["integer"];
        self.follow = {}
        self.errorinfo = {"base": "error", "no prog": "\"program\" is expected", "no program": "\"program\" is expected",
                     "no id": "an id is expected", "no ;": "\";\" is expected", "no const": "\"const\" is expected",
                     "no :=": "\":=\" is expected", "no num": "a num is expected", "no var": "\"var\" is expected",
                     "no proc": "\"procedure\" is expected", "no procedure": "\"procedure\" is expected",
                     "no (": "\"(\" is expected", "no )": "\")\" is expected",
                     "no begin": "\"begin\" is expected", "no end": "\"end\" is expected",
                     "no statement": "a statement is expected", "no then": "\"then\" is expected",
                     "no do": "\"do\" is expected", "no lexp": "a lexp is expected", "no lop": "a lop is expected",
                     "no aop": "an aop is expected", "no mop": "a mop is expected"}
        self.reportedi = {}  # 已被找出是拼写错误的下标以及正确的词/已经报错过的词法单元索引
    def prog(self):

        # < prog > → program < id >； < block >

        #处理program
        if self.find("program",["id"]) ==False:
            return
        if self.find("program",["id"]) !="miss":#非缺失才跳过
            self.lex.advance()#跳过program
        #处理id
        if self.find("id",[";"])==False:
            return
        if self.find("id",[";"])!="miss":
            self.id()
        #处理;
        if self.find(";",["block"])==False:
            return
        if self.find(";",["block"])!="miss":#缺失不跳过
            self.lex.advance()
        #由于block的情况特殊，很多东西可有可无，所以直接进入block，缺失或错误会在block中处理
        self.block()

    def block(self):

        # < block > → [ < condecl >][ < vardecl >][ < proc >] < body >
        # 记录本层之前的数据量，返回时需恢复
        dx0 = self.dx
        #保存原符号表并创建新符号表
        self.dx = 4 #当前活动记录中的变量的相对地址，前四个分别为老BP,RA,display，形参个数

        #记录当前指令在代码段的位置
        jmpPoint = self.Codes.i
        self.Codes.gen("JMP", 0, 0) #产生无条件跳转指令

        lastSymbol = None
        if self.topTable != None:
            lastSymbol = self.topTable.GetLast()
            if lastSymbol.kind == "procedure": #为形参预留空间
                self.dx += lastSymbol.val
                self.procs.append([lastSymbol.name, lastSymbol.val, jmpPoint]) #存储该过程的参数个数及其语句起始位置

        # print("新建符号表")
        saved = self.topTable
        self.topTable = STable()
        self.topTable.MakeTable(saved)


        if self.find("condecl",["vardecl","proc","body"],False)==True:#缺失则不进入condecl
            self.condecl()
            if self.find("vardecl",["proc","body"],False)==True:
                self.vardecl()
                if self.find("proc",["body"],False)==True:
                    self.proc()
            elif self.find("proc",["body"])!=False:
                self.proc()

        elif self.find("vardecl",["proc","body"],False)==True:
            self.vardecl()
            if self.find("proc",["body"],False)==True:
                self.proc()

        elif self.find("proc",["body"],False)==True:
            self.proc()

        #此时代码段指针指向语句开始位置，回填JMP的目标地址
        self.Codes.backPatch(jmpPoint, self.Codes.i)
        # 分配存储空间代码
        self.Codes.gen("INT", 0, self.dx-self.topTable.GetExtraFormalParamNum()) #减去本层形参所占空间

        # 处理 <body>
        if self.find("body",["statement"]) == False:
            return
        if self.find("body", ["statement"]) !="miss":
            self.body()

        #产生返回指令
        self.Codes.gen("OPR", 0, 0)


        # 恢复原符号表
        # if lastSymbol != None:
        #     print(lastSymbol.name+"的符号表")
        # self.topTable.show()
        # print("释放符号表")
        self.topTable = saved
        self.dx = dx0 #恢复dx初值

    def condecl(self):

        # < condecl > → const < const > {, < const >};

        #self.lex.sym() == "const"或输入错误才能进入该函数
        self.lex.advance()
        if self.find("const",[",",";"])==False:
            return
        if self.find("const",[",",";"])!="miss":
            self.const()
        while self.lex.sym() == ',' or self.infirst("const"):
            if self.infirst("const"):#若下一字符是来自const，则缺失','
                self.error("no ,",False,True)
            else:
                self.lex.advance()
            if self.find("const",[",",";"])==False:
                return
            if self.find("const", [",", ";"])!="miss":
                self.const()
        #处理;
        if self.find(";",["vardecl","proc","body"])==False:
            return
        if self.find(";", ["vardecl", "proc", "body"]) != "miss":
            self.lex.advance()

    def const(self):

        # < const > → < id >: = < integer >

        id = "" #存放名字
        value = 0 #存放值
        #处理id
        if self.find("id",[":="])==False:
            return
        if self.find("id", [":="])!="miss":
            id = self.lex.sym()
            self.id()
        #处理:=
        if self.find(":=",["integer"])==False:
            return
        if self.find(":=", ["integer"])!="miss":
            self.lex.advance()
        #处理integer
        if self.find("integer",[",",";"]) == False:
            return
        if self.find("integer", [",", ";"])!="miss":
            value = eval(self.lex.sym())
            self.integer()

        #常量写入符号表
        self.topTable.Enter(name=id, kind="const", val=value)

    def vardecl(self):

        # < vardecl > → var < id > {, < id >};
        idlist = [] #存放已经定义的变量名
        id = "" #存放变量名
        line = 0 #存放行数
        formalId = self.topTable.GetFormalId() #形参名字表
        #self.lex.sym() == "var"或输入错误才能进入该函数
        self.lex.advance()
        if self.find("id",[",",";"])==False:
            return
        if self.find("id", [",", ";"])!="miss":
            id = self.lex.sym()
            line = self.lex.getline()[:-1]
            self.id()
        #变量名写入符号表(同时写入其相对地址)
        result = self.topTable.GetSymbol(id)
        if result!=None and result.kind == "const":#该id已经被定义为常量
            self.isiserror = 1
            str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} has been defined as a const\033[0m"
            print(str.format(line, id))
        elif formalId != None and id in formalId[:-1]:#该id已经被定义为函数形参
            self.isiserror = 1
            str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} has been defined as a formal parameter in " \
                  "procedure {2:^10}\033[0m"
            print(str.format(line, id, formalId[-1]))
        self.topTable.Enter(id, "var", self.level, self.dx)
        self.dx += 1
        idlist.append(id)

        while self.lex.sym() == ',' or self.infirst("id"):
            if self.infirst("id"):
                self.error("no ,",False,True)
            else:
                self.lex.advance()
            if self.find("id",[",",";"])==False:
                return
            if self.find("id", [",", ";"])!="miss":
                id = self.lex.sym()
                line = self.lex.getline()[:-1]
                self.id()
            result = self.topTable.GetSymbol(id)
            if result != None and result.kind == "const":  # 该id已经被定义为常量
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} has been defined as a const\033[0m"
                print(str.format(line, id))
            elif formalId != None and id in formalId[:-1]:  # 该id已经被定义为函数形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} has been defined as a formal parameter in " \
                      "procedure {2:^10}\033[0m"
                print(str.format(line, id, formalId[-1]))
            elif id  in idlist:  # 变量已经被定义
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} has been defined\033[0m"
                print(str.format(line, id))
            else:# 未被定义过
                # 变量名写入符号表(同时写入其相对地址)
                self.topTable.Enter(id, "var", self.level, self.dx)
                self.dx += 1
                idlist.append(id)


        #处理;
        if self.find(";",["proc","body"])==False:
            return
        if self.find(";", ["proc", "body"]) != "miss":
            self.lex.advance()

    def proc(self):

        # < proc > → procedure < id >（[ < id > {, < id >}]）; < block > {; < proc >}
        paramnum = 0 #参数个数
        proid = ""#记录procedure的名字
        id = ""
        #self.lex.sym() == "procedure"或输入错误才能进入该函数
        self.lex.advance()
        if self.find("id",["("])==False:
            return
        if self.find("id", ["("])!="miss":
            proid = self.lex.sym()
            self.id()

        #处理(
        if self.find("(",["id",")"])==False:
            return
        if self.find("(", ["id", ")"])!="miss":
            self.lex.advance()
        #处理<id>
        if self.lex.gettype() == "标识符":
            id = self.lex.sym()
            self.id()
            paramnum += 1
            #将形参写入符号表
            self.topTable.Enter(id, "var", self.level+1, 4, 0, True) #是形参,在活动记录中偏移是4（前4个分别是SL,DL,RA和形参个数）
            self.dx += 1

            while self.lex.sym() == ',' or self.infirst("id"):
                if self.infirst("id"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("id",[",",")"])==False:
                    return
                if self.find("id", [",", ")"])!="miss":
                    id = self.lex.sym()
                    self.id()
                    paramnum += 1
                    # 将形参写入符号表
                    self.topTable.Enter(id, "var", self.level+1, 4+paramnum-1, 0, True)
                    self.dx += 1
        #处理)
        if self.find(")",[";"])==False:
            return
        if self.find(")", [";"])!="miss":
            self.lex.advance()
        #处理;
        if self.find(";",["block"])==False:
            return
        if self.find(";", ["block"]) != "miss":
            self.lex.advance()

        # 将procudure名字写入符号表(存入参数个数)
        self.topTable.Enter(proid, "procedure", self.level, self.Codes.i, paramnum)
        # 进入block嵌套层次+1
        self.level += 1
        #处理<block>
        if self.find("block",["const","id",":="]) == False:
            return
        if self.find("block", ["const","id",":="])!="miss":

            self.block()
        self.level -= 1  # 一个函数结束嵌套层次-1

        while self.lex.sym() == ';' or self.infirst("proc"):
            if self.infirst("proc"):
                self.error("no ;",False,True)
            self.lex.advance()
            if self.find("proc",["body",";"]) == False:
                return
            if self.find("proc", ["body", ";"])!="miss":
                self.proc()

    def body(self):

        # < body > → begin < statement > {; < statement >}end

        #self.lex.sym() == "begin"或输入错误才能进入函数
        self.lex.advance()
        if self.find("statement",["end",";"])==False:
            return
        if self.find("statement", ["end", ";"])!="miss":
            self.statement()
        while self.lex.sym() == ';':
            self.lex.advance()
            if self.find("statement", ["end", ";"])==False:
                return
            if self.find("statement", ["end", ";"])!="miss":
                self.statement()

        #处理end
        if self.find("end")==False:
            self.error("no end",False,True)
            return
        self.lex.advance()

    def statement(self):

        # < statement > → < id >: = < exp >
        # | if < lexp > then < statement >[else < statement >]
        # | while < lexp > do < statement >
        # | call < id >（[ < exp > {, < exp >}]）
        # | < body >
        # | read( < id > {， < id >})
        # | write( < exp > {, < exp >})

        # < id >: = < exp >
        if self.lex.gettype() == "标识符":
            id = self.lex.sym() #记录id
            line = self.lex.getline()[:-1] #记录行号
            self.id()
            #从符号表中查找该id的表项
            result = self.topTable.GetSymbol(id)
            if result == None:#该id未定义或被定义为形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} is not defined\033[0m"
                print(str.format(line, id))
            elif result.form == True and result.level > self.level:#调用内层形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                print(str.format(line, id))
            elif result.kind != "var":#该id被定义为变量以外的类型
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} is not correctly defined, expect var, got " \
                      "{2:^3}\ge033[0m"
                print(str.format(line, id, result.kind))

            #处理:=
            if self.find(":=",["exp"])==False:
                return
            if self.find(":=", ["exp"])!="miss":
                self.lex.advance()
            #处理<exp>
            if self.find("exp",[";","end"])==False:
                return
            if self.find("exp", [";", "end"])!="miss":
                self.exp()
            #生成代码完成赋值
            self.Codes.gen("STO", self.level-result.level, result.adr)

        # if < lexp > then < statement >[else < statement >]
        elif self.lex.sym() == "if" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="if":#输入错误
            self.lex.advance()
            if self.find("lexp",["then"])==False:
                return
            if self.find("lexp", ["then"])!="miss":
                self.lexp()
            #处理then
            if self.find("then",["statement"])==False:
                return
            if self.find("then", ["statement"])!="miss":
                self.lex.advance()

            jmpPoint = self.Codes.i #记录跳转指令地址
            self.Codes.gen("JPC", 0, 0)

            #处理<statement>
            if self.find("statement",["else",";","end"]) == False:
                return
            if self.find("statement", ["else", ";", "end"])!="miss":
                self.statement()

            # 回填跳转指令的目标地址
            self.Codes.backPatch(jmpPoint, self.Codes.i)

            if self.lex.sym() == "else":
                self.Codes.backPatch(jmpPoint, self.Codes.i+1) #进入else部分
                self.lex.advance()

                # 记录跳转指令指针产生跳转指令
                tmpPoint = self.Codes.i
                self.Codes.gen("JMP", 0, 0)# 条件语句结束部分

                if self.find("statement",[";","end"]) == False:
                    return
                if self.find("statement", [";", "end"])!="miss":
                    self.statement()

                # 回填跳转指令
                self.Codes.backPatch(tmpPoint, self.Codes.i)

        # while < lexp > do < statement >
        elif self.lex.sym() == "while" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="while":
            self.lex.advance()
            conditionPoint = self.Codes.i  # 记录条件判断地址
            if self.find("lexp",["do"])==False:
                return
            if self.find("lexp", ["do"])!="miss":
                self.lexp()
            #处理do
            if self.find("do",["statement"])==False:
                return
            if self.find("do", ["statement"])!="miss":
                self.lex.advance()

            jmpPoint = self.Codes.i #记录条件转移语句的位置
            # 生成条件转移语句
            self.Codes.gen("JPC", 0, 0)
            #处理<statement>
            if self.find("statement",[";","end"]) == False:
                return
            if self.find("statement", [";", "end"])!="miss":
                self.statement()

            # 生成返回条件判断的语句
            self.Codes.gen("JMP", 0, conditionPoint)
            # 回填循环结束的地址
            self.Codes.backPatch(jmpPoint, self.Codes.i) #此时的i是循环结束后的语句地址

        # call < id >（[ < exp > {, < exp >}]）
        elif self.lex.sym() == "call" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="call":
            paramnum = 0#记录调用时使用的参数个数
            id = ""  #记录函数名
            line = 0 #记录行
            self.lex.advance()
            if self.find("id",["("])==False:
                return
            if self.find("id", ["("])!="miss":
                id = self.lex.sym()
                line = self.lex.getline()[:-1]
                self.id()
            # 从符号表中查找该函数
            result = self.topTable.GetSymbol(id)
            if result == None:#未找到函数（函数未定义）
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tprocedure {1:^10} is not defined\033[0m"
                print(str.format(line, id))

            #处理(
            if self.find("(",["exp",")"])==False:
                return
            if self.find("(", ["exp", ")"])!="miss":
                self.lex.advance()
            #处理<exp>
            if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
                self.exp()
                paramnum += 1
                # # 传参
                # param = self.topTable.table[self.topTable.table.index(result)-t]#找到参数
                # t -= 1
                # self.Codes.gen("STO", 0, param.adr)
                while self.lex.sym() == ',' or self.infirst("exp"):
                    if self.infirst("exp"):
                        self.error("no ,",False,True)
                    else:
                        self.lex.advance()
                    if self.find("exp",[",",")"])==False:
                        return
                    if self.find("exp", [",", ")"])!="miss":
                        self.exp()
                        paramnum += 1
                        # # 传参
                        # param = self.topTable[self.topTable.index(result) - t]  # 找到参数
                        # t -= 1
                        # self.Codes.gen("STO", 0, param.adr)
            #处理)
            if self.find(")")==False:
                return
            self.lex.advance()

            if paramnum != result.val:#参数个数不匹配
                self.iserror = 1
                str="\033[1;31;0mSyntax Error:\tline:{0:<5}\tThe num of params of procedure {1:^10} is not correct" \
                    ",expect{2:^5}, got {3:^5}\033[0m"
                print(str.format(line, id, result.val, paramnum))

            # 生成代码
            self.Codes.gen("CAL", self.level - result.level, result.adr)

        # < body >
        elif self.lex.sym() in self.first["body"] or self.lex.i in self.reportedi:
            self.body()

        # read( < id > {， < id >})
        elif self.lex.sym() == "read" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="read":
            id = "" #记录id的名字
            line = 0 #记录id的行号
            self.lex.advance()
            #处理(
            if self.find("(",["id"])==False:
                return
            if self.find("(", ["id"])!="miss":
                self.lex.advance()
            #处理<id>
            if self.find("id",[",",")"])==False:
                return
            if self.find("id", [",", ")"])!="miss":
                id = self.lex.sym()
                line = self.lex.getline()[:-1]
                self.id()
            #从符号表中查找id
            result = self.topTable.GetSymbol(id)
            if result == None:#id未定义或被定义为形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                print(str.format(line, id))
            elif result.form == True and result.level > self.level:#调用内层形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                print(str.format(line, id))
            elif result.kind != "var":#id类型不是变量
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not variable\033[0m"
                print(str.format(line, id))
            else:
                #生成读入数据并存储到变量的代码
                self.Codes.gen("RED", self.level-result.level, result.adr)

            while self.lex.sym() == ',' or self.infirst("id"):
                if self.infirst("id"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("id",[",",")"]) == False:
                    return
                if self.find("id", [",", ")"])!="miss":
                    id = self.lex.sym()
                    line = self.lex.getline()[:-1]
                    self.id()
                # 从符号表中查找id
                result = self.topTable.GetSymbol(id)
                if result == None:  # id未定义或被定义为形参
                    self.iserror = 1
                    str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:<10} is not defined\033[0m"
                    print(str.format(line, id))
                elif result.form == True and result.level > self.level:  # 调用内层形参
                    self.iserror = 1
                    str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                    print(str.format(line, id))
                else:
                    # 生成读入数据并存储到变量的代码
                    self.Codes.gen("RED", self.level - result.level, result.adr)

            #处理)
            if self.find(")",[";","end"])==False:
                return
            if self.find(")", [";", "end"])!="miss":
                self.lex.advance()

        # write( < exp > {, < exp >})
        elif self.lex.sym() == "write" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="write":
            self.lex.advance()
            #处理(
            if self.find("(",["exp"])==False:
                return
            if self.find("(", ["exp"])!="miss":
                self.lex.advance()
            #处理<exp>
            if self.find("exp",[",",")"])==False:
                return
            if self.find("exp",[",", ")"])!="miss":
                self.exp()

            # 生成输出指令
            self.Codes.gen("WRT", 0, 0)
            while self.lex.sym() == ',' or self.infirst("exp"):
                if self.infirst("exp"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("exp",[",",")"]) == False:
                    return
                if self.find("exp", [",", ")"])!="miss":
                    self.exp()
                # 生成输出指令
                self.Codes.gen("WRT", 0, 0)
            #处理)
            if self.find(")",[";","end"])==False:
                return
            if self.find(")", [";", "end"])!="miss":
                self.lex.advance()

            # 输出换行指令
            self.Codes.gen("OPR", 0, 15)

    def lexp(self):

        # < lexp > → < exp > < lop > < exp > | odd < exp >

        if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
            if self.find("exp",["lop"])==False:
                return
            if self.find("exp", ["lop"])!="miss":
                self.exp()
            if self.find("lop",["exp"])==False:
                return
            if self.find("lop", ["exp"])!="miss":
                lop = self.lex.sym()
                self.lop()
            if self.find("exp",["then","do"])==False:
                return
            if self.find("exp", ["then", "do"])!="miss":
                self.exp()
            # 根据lop的不同值产生对应的判断指令
            self.Codes.gen("OPR", 0, self.first["lop"].index(lop)+8) # 等于对应8，不等对应9，以此类推

        elif self.lex.sym() == "odd":
            self.lex.advance()
            if self.find("exp",["then","do"])==False:
                return
            if self.find("exp", ["then", "do"])!="miss":
                self.exp()
            # 判断奇偶指令
            self.Codes.gen("ORP", 0, 6)

    def exp(self):

        # < exp > → [+ | -] < term > { < aop > < term >}
        # 处理+/-
        sign = self.lex.sym() #记录加减符号(正负)
        if self.lex.sym() in ["+","-"]:
            self.lex.advance()

        # 处理 <term>
        if self.find("term",["aop"])==False:
            return
        if self.find("term", ["aop"])!="miss":
            self.term()

        if sign == "-":#负号生成取反指令
            self.Codes.gen("OPR", 0, 1)

        while self.lex.sym() in self.first["aop"]:
            aop = self.lex.sym()
            if self.find("aop",["factor"])==False:
                return
            if self.find("aop", ["factor"])!="miss":
                self.aop()
            if self.find("term",["then","do"]) == False:
                return
            if self.find("term",["then","do"])!="miss":
                self.term()

            # 根据aop生成对应的运算指令
            if aop == "+":
                self.Codes.gen("OPR", 0, 2)
            else:
                self.Codes.gen("OPR", 0, 3)

    def term(self):

        # < term > → < factor > { < mop > < factor >}

        if self.find("factor")==False:
            return
        self.factor()
        while self.lex.sym() in self.first["mop"]:
            if self.find("mop",["factor"]) == False:
                return
            if self.find("mop", ["factor"])!="miss":
                mop = self.lex.sym()
                self.mop()
            if self.find("factor",["aop","then","do"]) == False:
                return
            if self.find("factor", ["aop", "then", "do"])!="miss":
                self.factor()

            # 根据mop生成对应运算指令
            self.Codes.gen("OPR", 0, self.first["mop"].index(mop)+4) #乘法对应4，除法对应5

    def factor(self):

        # < factor >→ < id > | < integer > | (< exp >)

        id = "" #记录id名称
        line = 0 #记录id行号
        if self.lex.gettype() == "标识符":
            id = self.lex.sym()
            line = self.lex.getline()[:-1]
            self.id()
            result = self.topTable.GetSymbol(id)
            if result == None:#id未定义或被定义为形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                print(str.format(line, id))
            elif result.form == True and result.level > self.level:#调用内层形参
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^5} is not defined\033[0m"
                print(str.format(line, id))
            elif result.kind not in ["const", "var"]:
                self.iserror = 1
                str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\tid {1:^10} is not correctly defined, expect var or const" \
                      ", got {2:^3}\033[0m"
                print(str.format(line, id, result.kind))
            else:
                #对应类型var或const生成对应代码
                if result.kind == "const":#将常量值放到栈顶
                    self.Codes.gen("LIT", 0, result.val)
                else:#将变量放到栈顶
                    self.Codes.gen("LOD", self.level-result.level, result.adr)

        elif self.lex.gettype() == "常数":
            num = eval(self.lex.sym())
            self.integer()
            self.Codes.gen("LIT", 0, num)# 将常数放到栈顶

        elif self.lex.sym() == '(':
            self.lex.advance()
            if self.find("exp",[")"])==False:
                return
            if self.find("exp", [")"])!="miss":
                self.exp()
            #处理)
            if self.find(")",["mop","then","do","aop"])==False:
                return
            if self.find(")", ["mop", "then", "do", "aop"])!="miss":
                self.lex.advance()

    def lop(self):

        # < lop > → = | <> | < | <= | > | >=

        if self.lex.sym() in self.first["lop"]:
            self.lex.advance()

    def aop(self):

        # < aop > → + | -

        if self.lex.sym() in self.first["aop"]:
            self.lex.advance()

    def mop(self):

        # <mop> → *|/

        if self.lex.sym() in self.first["mop"]:
            self.lex.advance()

    def id(self):

        # < id > → l{l | d}   （注：l表示字母）

        if self.lex.gettype() == "标识符":
            self.lex.advance()

    def integer(self):

        # < integer > → d{d}

        if self.lex.gettype() == "常数":
            self.lex.advance()

    def error(self,i="base",jump=True,miss=False):
        # 报错函数，jump为真时下移一步
        # miss为True时说明缺失的是不在errorinfo中的终结符，如','
        if jump:
            self.lex.advance()
        elif miss and i not in self.errorinfo.keys():
            self.iserror = 1
            str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\t{1:>5} is expected\033[0m"
            print(str.format(self.lex.getpreline()[:len(self.lex.getpreline()) - 1], i.split(" ")[1]))
        else:
            self.iserror = 1
            str = "\033[1;31;0mSyntax Error:\tline:{0:<5}\t{1:<5}\t{2:<5}\033[0m"
            print(str.format(self.lex.getline()[:-1], self.lex.sym(), self.errorinfo[i]))


    def infirst(self,ftype):#返回当前词是否在非终结符ftype的first集合中
        result=True
        if ftype == "id" or ftype == "const":
            result = self.lex.gettype() == "标识符"
        elif ftype == "integer":
            result = self.lex.gettype() == "常数"
        elif ftype == "statement":
            result = self.lex.sym() in self.first[ftype] or self.infirst("id")
        elif ftype == "lexp" or ftype == "exp" or ftype == "term" or ftype == "factor":
            #他们的first集合包含id和integer的first集合
            result = self.lex.sym() in self.first[ftype] or self.infirst("id") or self.infirst("integer")
        else:
            result = self.lex.sym() in self.first[ftype]
        return result
    def find(self,ftype,follow=[],neccessary=True):
        # 跳过不在非终结符 ftype 的first集合中的单词（或相似单词）并输出错误,返回是否找到 ftype 的first集合;
        # 若在找到ftype的first集合中的单词前找到follow中的first集合中的单词，则认为缺失了ftype,返回"miss"
        # neccessary表示是否需要报错（缺失是否致命，eg:vardecl可有可无）
        # 若字符串相似度大于0.5，则认为是输入错误，也考虑成找到的情况
        result = True
        misspelled=False #是否拼写错误
        rightword = "" #出现拼写错误时的正确单词
        if self.lex.sym() == False:#已到结尾
            result = False

        elif ftype in self.first.keys():#是非终结符
            while self.infirst(ftype)==False:
                if self.lex.sym() == False:  # 已到结尾
                    return False
                if self.infirst(ftype)==False:
                    for str in self.first[ftype]:
                        # 比较当前词和应有词的相似度
                        if difflib.SequenceMatcher(None, self.lex.sym(), str).quick_ratio()>=0.6:
                            # 拼写错误，报错并认为这个单词是正确的，继续向下分析
                            rightword = str#正确的单词
                            if self.lex.i not in self.reportedi.keys():
                                self.error("no " + rightword,False)
                                self.reportedi[self.lex.i]=rightword
                            return True
                    # 检测当前读取到的字符是否是follow中的字符，若是则缺失当前所需的终结符
                    if len(follow)>0:
                        for foll in follow:
                            flag = False
                            if foll not in self.first.keys():#终结符
                                if self.lex.sym() == foll:
                                    flag = True
                            elif self.infirst(foll):#在foll的first集合中
                                    flag = True
                            if flag:
                                if self.lex.i not in self.reportedi.keys() and neccessary:
                                    self.error("no " + ftype, False, True)
                                    self.reportedi[self.lex.i] = self.lex.sym()
                                return "miss"
                    self.iserror = 1
                    pstr = "\033[1;31;0mSyntax Error\tline:{0:<5}\t\tillegal symbol: {1:<10}\033[0m"
                    print(pstr.format(self.lex.getline()[:-1], self.lex.sym()))
                self.lex.advance()
            result = True
        else:#终结符
            while self.lex.sym() != ftype:
                if self.lex.sym() == False:  # 已到结尾
                    return False
                if self.lex.sym() != ftype:
                    #检测是否是拼写错误
                    if difflib.SequenceMatcher(None, self.lex.sym(), ftype).quick_ratio() >= 0.6:
                        if self.lex.i not in self.reportedi.keys():
                            self.error("no " + ftype, False)
                            self.reportedi[self.lex.i] = ftype
                        return True
                    #检测当前读取到的字符是否是follow中的字符，若是则缺失当前所需的终结符
                    if len(follow) > 0:
                        for foll in follow:
                            flag = False
                            if foll not in self.first.keys():
                                if self.lex.sym() == foll:
                                    flag = True
                            elif self.infirst(foll):
                                flag = True
                            if flag:
                                if self.lex.i not in self.reportedi.keys() and neccessary:
                                    self.error("no " + ftype, False,True)
                                    self.reportedi[self.lex.i] = self.lex.sym()
                                return "miss"
                    self.iserror = 1
                    pstr = "\033[1;31;0mSyntax Error\tline:{0:<5}\t\tillegal symbol: {1:<10}\033[0m"
                    print(pstr.format(self.lex.getline()[:-1], self.lex.sym()))
                self.lex.advance()
            result = True
        return result

gram = parser()
gram.prog()
# print(gram.procs)
if gram.iserror != 1:
    gram.Codes.show()
    gram.Codes.interpreter(gram.procs)