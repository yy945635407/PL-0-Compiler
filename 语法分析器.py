class lexical:
    i = 0
    lines = []

    def __init__(self):
        f = open("result.txt")
        self.lines = f.readlines()
        f.close()
    def SYM(self):
        if self.i == len(self.lines):
            return False
        return self.lines[self.i].split('.')[0]
    def gettype(self):
        return self.lines[self.i].split('.')[1]
    def getline(self):
        return self.lines[self.i].split('.')[2]
    def advance(self):
        self.i += 1

class parser:
    lex = lexical()
    first={"prog":["program"],"block":["const","var","procedure","begin"],"condecl":["const"],
           "vardecl":["var"],"proc":["procedure"]
           ,"body":["begin"],"statement":["if","while","call","begin","read","write"],"lexp":[],"exp":["+","-"],
           "term":[],"factor":[],"lop":["=","<>",
          "<","<=",">",">="],"aop":["+","-"],"mop":["*","/"]}
    follow = {}
    errorinfo={"base":"error","no prog":"\"program\" is expected","no id":"an id is expected",
               "no ;":"\";\" is expected","no const":"\"const\" is expected","no :=":"\":=\" is expected",
               "no num":"a num is expected","no var":"\"var\" is expected","no proc":"\"procedure\" is expected",
               "no (":"\"(\" is expected","no )":"\")\" is expected","no begin":"\"begin\" is expected",
               "no end":"\"end\" is expected","no statement":"a statement is expected","no then":"\"then\" is expected",
               "no do":"\"do\" is expected","no lexp":"a lexp is expected","no lop":"a lop is expected",
               "no aop": "an aop is expected","no mop":"a mop is expected"}
    def prog(self):
        if self.lex.SYM() != "program":#program输入错误
            self.error("no prog")
        else:#是program
            self.lex.advance()
        if self.find("id")==False:
            return
        #跳过不在id的first集合中的词
        self.id()
        if self.lex.SYM() != ";":#缺失分号
            self.error("no ;",False)
        else:#是分号
            self.lex.advance()
        if self.find("block")==False:
            return
        #跳过不在id的block集合中的词
        self.block()

    def block(self):
        if self.lex.SYM() in self.first["condecl"]:
            self.condecl()
            if self.lex.SYM() in self.first["vardecl"]:
                self.vardecl()
                if self.lex.SYM() in self.first["proc"]:
                    self.proc()
            elif self.lex.SYM() in self.first["proc"]:
                self.proc()

        elif self.lex.SYM() in self.first["vardecl"]:
            self.vardecl()
            if self.lex.SYM() in self.first["proc"]:
                self.proc()

        elif self.lex.SYM() in self.first["proc"]:
            self.proc()
        if self.find("body") == False:
            return
        self.body()

    def condecl(self):
        #self.lex.SYM() == "const"才能进入该函数
        self.lex.advance()
        if self.find("const")==False:
            return
        self.const()
        while self.lex.SYM() == ',':
            self.lex.advance()
            if self.find("const")==False:
                return
            self.const()
        if self.lex.SYM() !=';':#缺失分号
            self.error("no ;",False)
        else:
            self.lex.advance()

    def const(self):
        self.id()
        if self.lex.SYM() == ":=":
            self.lex.advance()
            if self.find("integer")==False:
                return
            self.integer()
        else:#缺失:=
            self.error("no :=")

    def vardecl(self):
        #self.lex.SYM() == "var"才能进入该函数
        self.lex.advance()
        if self.find("id")==False:
            return
        self.id()
        while self.lex.SYM() == ',':
            self.lex.advance()
            if self.find("id")==False:
                return
            self.id()
        if self.lex.SYM() != ';':#缺失;
            self.error("no ;",False)
        else:
            self.lex.advance()

    def proc(self):
        #self.lex.SYM() == "procedure"才能进入该函数
        self.lex.advance()
        if self.find("id")==False:
            return
        self.id()
        if self.lex.SYM() == '(':
            self.lex.advance()
            if self.lex.gettype() == "标识符":
                self.id()
                while self.lex.SYM() == ',':
                    self.lex.advance()
                    self.id()
            if self.lex.SYM() == ')':
                self.lex.advance()
                if self.lex.SYM() == ';':
                    self.lex.advance()
                    if self.find("block")==False:
                        return
                    self.block()
                    while self.lex.SYM() == ';':
                        self.lex.advance()
                        if self.find("proc")==False:
                            return
                        self.proc()
                else:#缺失;
                    self.error("no ;",False)
            else:#缺失)
                self.error("no )",False)
        else:#缺失(
            self.error("no (",False)

    def body(self):
        #self.lex.SYM() == "begin"才能进入函数
        self.lex.advance()
        if self.find("statement")==False:
            return
        self.statement()
        while self.lex.SYM() == ';':
            self.lex.advance()
            if self.find("statement")==False:
                return
            self.statement()
        if self.lex.SYM() != "end":#end输入错误
            if self.lex.SYM() == False:
                return
            self.error("no end")
        else:
            self.lex.advance()

    def statement(self):
        if self.lex.gettype() == "标识符":
            self.id()
            if self.lex.SYM() == ":=":
                self.lex.advance()
                self.exp()
            else:#缺失:=
                self.error("no :=")
        elif self.lex.SYM() == "if":
            self.lex.advance()
            if self.find("lexp")==False:
                return
            self.lexp()
            if self.lex.SYM() == "then":
                self.lex.advance()
                if self.find("statement")==False:
                    return
                self.statement()
                if self.lex.SYM() == "else":
                    self.lex.advance()
                    if self.find("statement")==False:
                        return
                    self.statement()
            else:#缺失then
                self.error("no then")
        elif self.lex.SYM() == "while":
            self.lex.advance()
            if self.find("lexp")==False:
                return
            self.lexp()
            if self.lex.SYM() == "do":
                self.lex.advance()
                if self.find("statement")==False:
                    return
                self.statement()
            else:#缺失do
                self.error("no do")

        elif self.lex.SYM() == "call":
            self.lex.advance()
            if self.find("id")==False:
                return
            self.id()
            if self.lex.SYM() == '(':
                self.lex.advance()
                if self.lex.SYM() in self.first["exp"] or self.lex.gettype() == "标识符":
                    self.exp()
                    while self.lex.SYM() == ',':
                        self.lex.advance()
                        self.exp()
                if self.lex.SYM() != ')':#缺失)
                    self.error("no )",False)
                else:
                    self.lex.advance()
            else:#缺失(
                self.error("no (")
        elif self.lex.SYM() in self.first["body"]:
            self.body()
        elif self.lex.SYM() == "read":
            self.lex.advance()
            if self.lex.SYM() == '(':
                self.lex.advance()
                self.id()
                while self.lex.SYM() == ',':
                    self.lex.advance()
                    self.id()
                if self.lex.SYM() != ')':#缺失)
                    self.error("no )",False)
                else:
                    self.lex.advance()
            else:#缺失(
                self.error("no (")
        elif self.lex.SYM() == "write":
            self.lex.advance()
            if self.lex.SYM() == '(':
                self.lex.advance()
                self.exp()
                while self.lex.SYM() == ',':
                    self.lex.advance()
                    self.exp()
                if self.lex.SYM() != ')':#缺失)
                    self.error("no )",False)
                else:
                    self.lex.advance()
            else:#缺失(
                self.error("no (")

    def lexp(self):
        if self.lex.SYM() in self.first["exp"] or self.lex.gettype() == "标识符":
            self.exp()
            self.lop()
            self.exp()
        elif self.lex.SYM() == "odd":
            self.lex.advance()
            self.exp()
        else:#缺失lexp
            self.error("no lexp")

    def exp(self):
        if self.lex.SYM() in ["+","-"]:
            self.lex.advance()
        self.term()
        while self.lex.SYM() in self.first["aop"]:
            self.aop()
            self.term()

    def term(self):
        self.factor()
        while self.lex.SYM() in self.first["mop"]:
            self.mop()
            self.factor()

    def factor(self):
        if self.lex.gettype() == "标识符":
            self.id()
        elif self.lex.gettype() == "常数":
            self.integer()
        elif self.lex.SYM() == '(':
            self.lex.advance()
            self.exp()
            if self.lex.SYM() != ')':#缺失)
                self.error("no )",False)
            else:
                self.lex.advance()
        else:
            self.error()

    def lop(self):
        if self.lex.SYM() in self.first["lop"]:
            self.lex.advance()
        else:#缺失逻辑操作
            self.error("no lop")
    def aop(self):
        if self.lex.SYM() in self.first["aop"]:
            self.lex.advance()
        else:#缺失aop
            self.error("no aop")
    def mop(self):
        if self.lex.SYM() in self.first["mop"]:
            self.lex.advance()
        else:#缺失mop
            self.error("no mop")
    def id(self):
        if self.lex.gettype() == "标识符":
            self.lex.advance()
        else:#缺失id
            self.error("no id")
    def integer(self):
        if self.lex.gettype() == "常数":
            self.lex.advance()
        else:#缺失常数
            self.error("no num")
    def error(self,i="base",jump=True):
        print("line:"+self.lex.getline()[:len(self.lex.getline())-1]+"\t"+self.lex.SYM()+"\t"+self.errorinfo[i])
        if jump:
            self.lex.advance()
    def find(self,ftype):# 跳过不在非终结符 ftype 的first集合中的字符并输出错误,返回是否找到 ftype 的first集合
        result = True
        if self.lex.SYM() == False:#已到结尾
            result = False
        elif ftype == "id" or ftype == "const": #const和id的first集合相同
            while self.lex.gettype() != "标识符":
                if self.lex.gettype() != "标识符":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:" + self.lex.SYM())
                self.lex.advance()
        elif ftype =="integer":
            while self.lex.gettype() != "常数":
                if self.lex.gettype() != "常数":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:" + self.lex.SYM())
                self.lex.advance()
        elif ftype =="exp" or ftype == "lexp":
            while self.lex.SYM() not in self.first["exp"] and self.lex.gettype() != "标识符":
                if self.lex.SYM() not in self.first["exp"] and self.lex.gettype() != "标识符":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:" + self.lex.SYM())
                self.lex.advance()
        elif ftype == "statement":#statement的first集合包含id的first集合
            while self.lex.SYM() not in self.first["statement"] and self.lex.gettype() != "标识符":
                if self.lex.SYM() not in self.first["statement"] and self.lex.gettype() != "标识符":
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:" + self.lex.SYM())
                self.lex.advance()
        else:
            while self.lex.SYM() not in self.first[ftype]:
                if self.lex.SYM() not in self.first[ftype]:
                    print("line:" + self.lex.getline()[:len(self.lex.getline()) - 1] + "\t" + "非法符号:" + self.lex.SYM())
                self.lex.advance()
        return result

gram = parser()
gram.prog()