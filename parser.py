import difflib
class lexical:
    i = 0
    lines = []

    def __init__(self):
        f = open("result.txt")
        self.lines = f.readlines()
        f.close()
    def sym(self):#取词
        if self.i == len(self.lines):
            return False
        return self.lines[self.i].split('.')[0]
    def gettype(self):#得到类别
        return self.lines[self.i].split('.')[1]
    def getline(self):#得到行号
        return self.lines[self.i].split('.')[2]
    def getpreline(self):#得到前一个行号
        if self.i<len(self.lines) and self.getline() == "1\n":
            return "1\n"
        return self.lines[self.i-1].split('.')[2]
    def advance(self):
        self.i += 1

class parser:
    lex = lexical()
    first={"prog":["program"],"block":["const","var","procedure","begin"],"condecl":["const"],
           "vardecl":["var"],"proc":["procedure"]
           ,"body":["begin"],"statement":["if","while","call","begin","read","write"],"lexp":["odd","(","+","-"],
           "exp":["+","-","("],
           "term":["("],"factor":["("],"lop":["=","<>","<","<=",">",">="],"aop":["+","-"],"mop":["*","/"],
           "id":[],"integer":[],"const":[]}
    #note:
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
    follow = {}
    errorinfo={"base":"error","no prog":"\"program\" is expected","no program":"\"program\" is expected",
               "no id":"an id is expected","no ;":"\";\" is expected","no const":"\"const\" is expected",
               "no :=":"\":=\" is expected","no num":"a num is expected","no var":"\"var\" is expected",
               "no proc":"\"procedure\" is expected","no procedure":"\"procedure\" is expected","no (":"\"(\" is expected","no )":"\")\" is expected",
               "no begin":"\"begin\" is expected","no end":"\"end\" is expected",
               "no statement":"a statement is expected","no then":"\"then\" is expected",
               "no do":"\"do\" is expected","no lexp":"a lexp is expected","no lop":"a lop is expected",
               "no aop": "an aop is expected","no mop":"a mop is expected"}
    reportedi = {}#已被找出是拼写错误的下标以及正确的词
    def prog(self):
        #处理program
        if self.find("program",["id"]) ==False:
            return
        if self.find("program",["id"]) !="miss":#非缺失才跳过
            self.lex.advance()#跳过program
        #处理id
        if self.find("id",[";"])==False:
            return
        self.id()
        #处理;
        if self.find(";",["block"])==False:
            return
        if self.find(";",["block"])!="miss":#缺失不跳过
            self.lex.advance()
        #由于block的情况特殊，很多东西可有可无，所以直接进入block，缺失或错误会在block中处理
        self.block()

    def block(self):
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

        if self.find("body",["statement"]) == False:
            return
        if self.find("body", ["statement"]) !="miss":
            self.body()

    def condecl(self):
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
        #处理id
        if self.find("id",[":="])==False:
            return
        if self.find("id", [":="])!="miss":
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
            self.integer()

    def vardecl(self):
        #self.lex.sym() == "var"或输入错误才能进入该函数
        self.lex.advance()
        if self.find("id",[",",";"])==False:
            return
        if self.find("id", [",", ";"])!="miss":
            self.id()
        while self.lex.sym() == ',' or self.infirst("id"):
            if self.infirst("id"):
                self.error("no ,",False,True)
            else:
                self.lex.advance()
            if self.find("id",[",",";"])==False:
                return
            if self.find("id", [",", ";"])!="miss":
                self.id()
        #处理;
        if self.find(";",["proc","body"])==False:
            return
        if self.find(";", ["proc", "body"]) != "miss":
            self.lex.advance()

    def proc(self):
        #self.lex.sym() == "procedure"或输入错误才能进入该函数
        self.lex.advance()
        if self.find("id",["("])==False:
            return
        if self.find("id", ["("])!="miss":
            self.id()
        #处理(
        if self.find("(",["id",")"])==False:
            return
        if self.find("(", ["id", ")"])!="miss":
            self.lex.advance()
        #处理<id>
        if self.lex.gettype() == "标识符":
            self.id()
            while self.lex.sym() == ',' or self.infirst("id"):
                if self.infirst("id"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("id",[",",")"])==False:
                    return
                if self.find("id", [",", ")"])!="miss":
                    self.id()
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
        #处理<block>
        if self.find("block",["const","id",":="]) == False:
            return
        if self.find("block", ["const","id",":="])!="miss":
            self.block()
        while self.lex.sym() == ';' or self.infirst("proc"):
            if self.infirst("proc"):
                self.error("no ,",False,True)
            self.lex.advance()
            if self.find("proc",["body",";"]) == False:
                return
            if self.find("proc", ["body", ";"])!="miss":
                self.proc()

    def body(self):
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
        if self.lex.gettype() == "标识符":
            self.id()
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
            #处理<statement>
            if self.find("statement",["else",";","end"]) == False:
                return
            if self.find("statement", ["else", ";", "end"])!="miss":
                self.statement()
            if self.lex.sym() == "else":
                self.lex.advance()
                if self.find("statement",[";","end"]) == False:
                    return
                if self.find("statement", [";", "end"])!="miss":
                    self.statement()

        elif self.lex.sym() == "while" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="while":
            self.lex.advance()
            if self.find("lexp",["do"])==False:
                return
            if self.find("lexp", ["do"])!="miss":
                self.lexp()
            #处理do
            if self.find("do",["statement"])==False:
                return
            if self.find("do", ["statement"])!="miss":
                self.lex.advance()
            #处理<statement>
            if self.find("statement",[";","end"]) == False:
                return
            if self.find("statement", [";", "end"])!="miss":
                self.statement()

        elif self.lex.sym() == "call" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="call":
            self.lex.advance()
            if self.find("id",["("])==False:
                return
            if self.find("id", ["("])!="miss":
                self.id()
            #处理(
            if self.find("(",["exp",")"])==False:
                return
            if self.find("(", ["exp", ")"])!="miss":
                self.lex.advance()
            #处理<exp>
            if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
                self.exp()
                while self.lex.sym() == ',' or self.infirst("exp"):
                    if self.infirst("exp"):
                        self.error("no ,",False,True)
                    else:
                        self.lex.advance()
                    if self.find("exp",[",",")"])==False:
                        return
                    if self.find("exp", [",", ")"])!="miss":
                        self.exp()
            #处理)
            if self.find(")")==False:
                return
            self.lex.advance()

        elif self.lex.sym() in self.first["body"] or self.lex.i in self.reportedi:
            self.body()
        elif self.lex.sym() == "read" or self.lex.i in self.reportedi.keys() and self.reportedi[self.lex.i]=="read":
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
                self.id()
            while self.lex.sym() == ',' or self.infirst("id"):
                if self.infirst("id"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("id",[",",")"]) == False:
                    return
                if self.find("id", [",", ")"])!="miss":
                    self.id()
            #处理)
            if self.find(")",[";","end"])==False:
                return
            if self.find(")", [";", "end"])!="miss":
                self.lex.advance()

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
            while self.lex.sym() == ',' or self.infirst("exp"):
                if self.infirst("exp"):
                    self.error("no ,",False,True)
                else:
                    self.lex.advance()
                if self.find("exp",[",",")"]) == False:
                    return
                if self.find("exp", [",", ")"])!="miss":
                    self.exp()
            #处理)
            if self.find(")",[";","end"])==False:
                return
            if self.find(")", [";", "end"])!="miss":
                self.lex.advance()

    def lexp(self):
        if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
            if self.find("exp",["lop"])==False:
                return
            if self.find("exp", ["lop"])!="miss":
                self.exp()
            if self.find("lop",["exp"])==False:
                return
            if self.find("lop", ["exp"])!="miss":
                self.lop()
            if self.find("exp",["then","do"])==False:
                return
            if self.find("exp", ["then", "do"])!="miss":
                self.exp()
        elif self.lex.sym() == "odd":
            self.lex.advance()
            if self.find("exp",["then","do"])==False:
                return
            if self.find("exp", ["then", "do"])!="miss":
                self.exp()

    def exp(self):
        if self.lex.sym() in ["+","-"]:
            self.lex.advance()

        if self.find("term",["aop"])==False:
            return
        if self.find("term", ["aop"])!="miss":
            self.term()
        while self.lex.sym() in self.first["aop"]:
            if self.find("aop",["factor"])==False:
                return
            if self.find("aop", ["factor"])!="miss":
                self.aop()
            if self.find("term",["then","do"]) == False:
                return
            if self.find("term",["then","do"])!="miss":
                self.term()

    def term(self):
        if self.find("factor")==False:
            return
        self.factor()
        while self.lex.sym() in self.first["mop"]:
            if self.find("mop",["factor"]) == False:
                return
            if self.find("mop", ["factor"])!="miss":
                self.mop()
            if self.find("factor",["aop","then","do"]) == False:
                return
            if self.find("factor", ["aop", "then", "do"])!="miss":
                self.factor()

    def factor(self):
        if self.lex.gettype() == "标识符":
            self.id()
        elif self.lex.gettype() == "常数":
            self.integer()
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
        if self.lex.sym() in self.first["lop"]:
            self.lex.advance()

    def aop(self):
        if self.lex.sym() in self.first["aop"]:
            self.lex.advance()

    def mop(self):
        if self.lex.sym() in self.first["mop"]:
            self.lex.advance()

    def id(self):
        if self.lex.gettype() == "标识符":
            self.lex.advance()

    def integer(self):
        if self.lex.gettype() == "常数":
            self.lex.advance()

    def error(self,i="base",jump=True,miss=False):
        # 报错函数，jump为真时下移一步
        # miss为True时说明缺失的是不在errorinfo中的终结符，如','
        if jump:
            self.lex.advance()
        elif miss:
            print("line:" + self.lex.getpreline()[:len(self.lex.getpreline()) - 1] + "\t\"" + i.split(" ")[1]
                  +"\" is expected")
        else:
            print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + self.lex.sym() + "\t" +
                self.errorinfo[i])


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
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" +
                              "非法符号:"+self.lex.sym())
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
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" +
                          "非法符号:" + self.lex.sym())
                self.lex.advance()
            result = True
        return result

gram = parser()
gram.prog()
