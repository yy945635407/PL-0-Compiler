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
    def getpreline(self):#得到上一个词的行号
        return self.lines[self.i-1].split('.')[2]
    def gettype(self):#得到类别
        return self.lines[self.i].split('.')[1]
    def getline(self):#得到行号
        return self.lines[self.i].split('.')[2]
    def advance(self):
        self.i += 1

class parser:
    lex = lexical()
    first={"prog":["program"],"block":["const","var","procedure","begin"],"condecl":["const"],
           "vardecl":["var"],"proc":["procedure"]
           ,"body":["begin"],"statement":["if","while","call","begin","read","write"],"lexp":["odd","(","+","-"],
           "exp":["+","-","("],
           "term":["("],"factor":["("],"lop":["=","<>","<","<=",">",">="],"aop":["+","-"],"mop":["*","/"]}
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
    errorinfo={"base":"error","no prog":"\"program\" is expected","no id":"an id is expected",
               "no ;":"\";\" is expected","no const":"\"const\" is expected","no :=":"\":=\" is expected",
               "no num":"a num is expected","no var":"\"var\" is expected","no proc":"\"procedure\" is expected",
               "no (":"\"(\" is expected","no )":"\")\" is expected","no begin":"\"begin\" is expected",
               "no end":"\"end\" is expected","no statement":"a statement is expected","no then":"\"then\" is expected",
               "no do":"\"do\" is expected","no lexp":"a lexp is expected","no lop":"a lop is expected",
               "no aop": "an aop is expected","no mop":"a mop is expected"}
    reportedi = []#已经报错的index
    def prog(self):
        #处理program
        if self.lex.sym() != "program":
            if difflib.SequenceMatcher(None,self.lex.sym(),"program").quick_ratio() >= 0.5:#错误段与program相似，则是输入错误
                self.error("no prog", True)
            else:#缺失program
                self.error("no prog",False)
        else:#是program
            self.lex.advance()
        if self.find("id")==False:
            return
        #跳过不在id的first集合中的词
        self.id()
        if self.lex.sym() != ";":#缺失分号
            self.error("no ;",False)
        else:#是分号
            self.lex.advance()
        if self.find("block")==False:
            return
        #跳过不在id的block集合中的词
        self.block()

    def block(self):
        if self.lex.sym() in self.first["condecl"]:
            self.condecl()
            if self.lex.sym() in self.first["vardecl"]:
                self.vardecl()
                if self.lex.sym() in self.first["proc"]:
                    self.proc()
            elif self.lex.sym() in self.first["proc"]:
                self.proc()

        elif self.lex.sym() in self.first["vardecl"]:
            self.vardecl()
            if self.lex.sym() in self.first["proc"]:
                self.proc()

        elif self.lex.sym() in self.first["proc"]:
            self.proc()

        if self.find("body") == False:
            return
        self.body()

    def condecl(self):
        #self.lex.sym() == "const"才能进入该函数
        self.lex.advance()
        if self.find("const")==False:
            return
        self.const()
        while self.lex.sym() == ',':
            self.lex.advance()
            if self.find("const")==False:
                return
            self.const()
        if self.lex.sym() !=';':#缺失分号
            self.error("no ;",False)
        else:
            self.lex.advance()

    def const(self):
        if self.find("id")==False:
            return
        self.id()
        if self.lex.sym() != ":=":
            if difflib.SequenceMatcher(None,self.lex.sym(),":=").quick_ratio()>=0.5:#输入错误
                self.error("no :=",True)
            else:
                self.error("no :=",False)
        else:#是:=
            self.lex.advance()
        if self.find("integer") == False:
            return
        self.integer()

    def vardecl(self):
        #self.lex.sym() == "var"才能进入该函数
        self.lex.advance()
        if self.find("id")==False:
            return
        self.id()
        while self.lex.sym() == ',':
            self.lex.advance()
            if self.find("id")==False:
                return
            self.id()
        if self.lex.sym() != ';':#缺失;
            self.error("no ;",False)
        else:
            self.lex.advance()

    def proc(self):
        #self.lex.sym() == "procedure"才能进入该函数
        self.lex.advance()
        if self.find("id")==False:
            return
        self.id()
        #处理(
        if self.lex.sym() == '(':
            self.lex.advance()
        else:#缺失(
            self.error("no (",False)
        #处理<id>
        if self.lex.gettype() == "标识符":
            self.id()
            while self.lex.sym() == ',':
                self.lex.advance()
                self.id()
        #处理)
        if self.lex.sym() == ')':
            self.lex.advance()
        else:  # 缺失)
            self.error("no )", False)
        #处理;
        if self.lex.sym() == ';':
            self.lex.advance()
        else:  # 缺失;
            self.error("no ;", False)
        #处理<block>
        if self.find("block") == False:
            return
        self.block()
        while self.lex.sym() == ';':
            self.lex.advance()
            if self.find("proc") == False:
                return
            self.proc()

    def body(self):
        #self.lex.sym() == "begin"才能进入函数
        self.lex.advance()
        if self.find("statement")==False:
            return
        self.statement()
        while self.lex.sym() == ';':
            self.lex.advance()
            if self.find("statement")==False:
                return
            self.statement()
        if self.lex.sym() != "end":#end输入错误
            if self.lex.sym() == False:
                return
            self.error("no end")
        else:
            self.lex.advance()

    def statement(self):
        if self.lex.gettype() == "标识符":
            self.id()
            #处理:=
            if self.lex.sym() == ":=":
                self.lex.advance()
            else:#缺失:=
                self.error("no :=")
            #处理<exp>
            if self.find("exp")==False:
                return
            self.exp()

        elif self.lex.sym() == "if":
            self.lex.advance()
            if self.find("lexp")==False:
                return
            self.lexp()
            #处理then
            if self.lex.sym() == "then":
                self.lex.advance()
            else:#缺失then
                self.error("no then",False)
            #处理<statement>
            if self.find("statement") == False:
                return
            self.statement()
            if self.lex.sym() == "else":
                self.lex.advance()
                if self.find("statement") == False:
                    return
                self.statement()

        elif self.lex.sym() == "while":
            self.lex.advance()
            if self.find("lexp")==False:
                return
            self.lexp()
            #处理do
            if self.lex.sym() == "do":
                self.lex.advance()
            else:#缺失do
                self.error("no do",False)
            #处理<statement>
            if self.find("statement") == False:
                return
            self.statement()

        elif self.lex.sym() == "call":
            self.lex.advance()
            if self.find("id")==False:
                return
            self.id()
            #处理(
            if self.lex.sym() == '(':
                self.lex.advance()
            else:#缺失(
                self.error("no (",False)
            #处理<exp>
            if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
                self.exp()
                while self.lex.sym() == ',':
                    self.lex.advance()
                    if self.find("exp")==False:
                        return
                    self.exp()
            #处理)
            if self.lex.sym() != ')':  # 缺失)
                self.error("no )", False)
            else:
                self.lex.advance()

        elif self.lex.sym() in self.first["body"]:
            self.body()
        elif self.lex.sym() == "read":
            self.lex.advance()
            #处理(
            if self.lex.sym() == '(':
                self.lex.advance()
            else:#缺失(
                self.error("no (")
            #处理<id>
            if self.find("id")==False:
                return
            self.id()
            while self.lex.sym() == ',':
                self.lex.advance()
                if self.find("id") == False:
                    return
                self.id()
            #处理)
            if self.lex.sym() != ')':  # 缺失)
                self.error("no )", False)
            else:
                self.lex.advance()

        elif self.lex.sym() == "write":
            self.lex.advance()
            #处理(
            if self.lex.sym() == '(':
                self.lex.advance()
            else:#缺失(
                self.error("no (")
            #处理<exp>
            if self.find("exp")==False:
                return
            self.exp()
            while self.lex.sym() == ',':
                self.lex.advance()
                if self.find("exp") == False:
                    return
                self.exp()
            #处理)
            if self.lex.sym() != ')':  # 缺失)
                self.error("no )", False)
            else:
                self.lex.advance()

    def lexp(self):
        if self.lex.sym() in self.first["exp"] or self.lex.gettype() == "标识符":
            if self.find("exp")==False:
                return
            self.exp()
            if self.find("lop")==False:
                return
            self.lop()
            if self.find("exp")==False:
                return
            self.exp()
        elif self.lex.sym() == "odd":
            self.lex.advance()
            if self.find("lop")==False:
                return
            self.exp()

    def exp(self):
        if self.lex.sym() in ["+","-"]:
            self.lex.advance()

        if self.find("term")==False:
            return
        self.term()
        while self.lex.sym() in self.first["aop"]:
            if self.find("aop")==False:
                return
            self.aop()
            if self.find("term") == False:
                return
            self.term()

    def term(self):
        if self.find("factor")==False:
            return
        self.factor()
        while self.lex.sym() in self.first["mop"]:
            if self.find("mop") == False:
                return
            self.mop()
            if self.find("factor") == False:
                return
            self.factor()

    def factor(self):
        if self.lex.gettype() == "标识符":
            self.id()
        elif self.lex.gettype() == "常数":
            self.integer()
        elif self.lex.sym() == '(':
            self.lex.advance()
            if self.find("exp")==False:
                return
            self.exp()
            if self.lex.sym() != ')':#缺失)
                self.error("no )",False)
            else:
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

    def error(self,i="base",jump=True):
        if jump:
            print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + self.lex.sym() + "\t" +
                  self.errorinfo[i])
            self.lex.advance()
        else:
            print("line:" + self.lex.getpreline()[:len(self.lex.getline()) - 1] + "\t\"" + i.split(" ")[1] +
                  "\" is expected")

    def find(self,ftype):# 跳过不在非终结符 ftype 的first集合中的字符并输出错误,返回是否找到 ftype 的first集合,
        # 若字符串相似度大于0.5，则认为是输入错误，也考虑成找到的情况
        result = True
        misspelled=False #是否拼写错误
        rightword = "" #出现拼写错误时的正确单词
        if self.lex.sym() == False:#已到结尾
            result = False

        elif ftype == "id" or ftype == "const": #const和id的first集合相同
            while self.lex.gettype() != "标识符":
                if self.lex.gettype() != "标识符":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:"+self.lex.sym())
                self.lex.advance()

        elif ftype =="integer":
            while self.lex.gettype() != "常数":
                if self.lex.gettype() != "常数":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:"+self.lex.sym())
                self.lex.advance()

        elif ftype == "statement":#statement的first集合包含id的first集合
            while self.lex.sym() not in self.first["statement"] and self.lex.gettype() != "标识符":
                if self.lex.sym() not in self.first["statement"] and self.lex.gettype() != "标识符":
                    for str in self.first[ftype]:
                        # 比较当前词和应有词的相似度
                        if difflib.SequenceMatcher(None, self.lex.sym(), str).quick_ratio()>=0.5:
                            misspelled=True
                            rightword = str
                            break
                    if misspelled==True:
                        if  self.lex.i not in self.reportedi:#未报过错则报错
                            self.error("no "+rightword,False)
                            self.reportedi.append(self.lex.i)
                        return True
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" +
                              "非法符号:"+self.lex.sym())
                self.lex.advance()

        elif ftype =="lexp" or ftype == "exp" or ftype=="term" or ftype=="factor":#他们的first集合包含id和integer的first集合
            while self.lex.sym() not in self.first[ftype] and self.lex.gettype() != "标识符" \
                    and self.lex.gettype() != "常数":
                if self.lex.sym() not in self.first[ftype] and self.lex.gettype() != "标识符" \
                        and self.lex.gettype() !="常数":
                    for str in self.first[ftype]:
                        # 比较当前词和应有词的相似度
                        if difflib.SequenceMatcher(None, self.lex.sym(), str).quick_ratio()>=0.5:
                            misspelled=True
                            rightword = str
                            break
                    if misspelled==True:
                        if self.lex.i not in self.reportedi:
                            self.error("no " + rightword,False)
                            self.reportedi.append(self.lex.i)
                        return True

                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" +
                              "非法符号:"+self.lex.sym())
                self.lex.advance()
        else:
            while self.lex.sym() not in self.first[ftype]:
                if self.lex.sym() not in self.first[ftype]:
                    for str in self.first[ftype]:
                        # 比较当前词和应有词的相似度
                        if difflib.SequenceMatcher(None, self.lex.sym(), str).quick_ratio()>=0.5:
                            misspelled=True
                            rightword = str
                            break
                    if misspelled==True:
                        if self.lex.i not in self.reportedi:
                            self.error("no " + rightword,False)
                            self.reportedi.append(self.lex.i)
                        return True

                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" +
                              "非法符号:"+self.lex.sym())
                self.lex.advance()
        return result

gram = parser()
gram.prog()