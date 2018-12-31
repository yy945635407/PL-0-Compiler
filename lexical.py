import random
class lexical:
    reservedWord = ["program","const","var","procedure","begin","end","if","then","while","do"
                   ,"call","read","write","odd"]
    calsign = ['+','-','*','/','=','<','>']
    rimsign=[';','(',')',',']
    id = []
    const = []
    content = ""
    end = ''
    line = 1
    col = 0
    i = 0
    ch = ''
    strToken = ""
    def __init__(self):#读文件，补结尾
        f = open("sourcecode.txt")
        self.content = f.read()
        f.close()
        self.end = random.randint(1,1000)
        self.end = chr(self.end)
        while self.end in self.content or self.end.isdigit() or self.end.isalpha(): #生成非字母或数字且源代码中未出现的结尾符号
            self.end = random.randint(1,1000)
            self.end = chr(self.end)
        self.content += self.end
        #print(self.end)

    def GetChar(self):#读取一个字符
        self.ch = self.content[self.i]
        self.i += 1
        self.col += 1

    def GetBC(self):#跳过空格
        while self.ch == ' ' or self.ch == '\n':
            if self.ch == '\n':
                self.line += 1
                self.col = 0
            self.GetChar()

    def Concat(self):
        self.strToken += self.ch

    def Reserve(self):
        if self.strToken in self.reservedWord:
            return self.reservedWord.index(self.strToken)
        else:
            return -1

    def Retract(self):
        self.i -= 1
        self.col -= 1

    def InsertId(self,strToken):
        self.id.append(strToken)

    def InsertConst(self,strToken):
        self.const.append(strToken)

    def analise(self):
        f = open("result.txt","w")
        while True:
            result = ""
            self.strToken=""
            self.GetChar()
            self.GetBC()
            if self.ch.isalpha():
                while self.ch.isalpha() or self.ch.isdigit():
                    self.Concat()
                    self.GetChar()
                    if self.i==len(self.content):
                        break
                self.Retract()
                code = self.Reserve()
                if code == -1:
                    self.InsertId(self.strToken)
                    result = self.strToken+".标识符."+str(self.line)+"\n"
                else:
                    result = self.strToken+".关键字."+str(self.line)+"\n"
            elif self.ch.isdigit():
                while self.ch.isdigit():
                    self.Concat()
                    self.GetChar()
                self.Retract()
                self.InsertConst(self.strToken)
                result = self.strToken+".常数."+str(self.line)+"\n"
            elif self.ch == ':':
                self.GetChar()
                if self.ch=='=':
                    result = ":=.算符."+str(self.line)+"\n"
                else:
                    self.Retract()
                    print("line", self.line, "col", self.col-1, ":error! : is unexpected!")
            elif self.ch == '<':
                self.GetChar()

                if self.ch=='>':
                    result = "<>.算符."+str(self.line)+"\n"
                elif self.ch == '=':
                    result = "<=.算符."+str(self.line)+"\n"
                else:
                    self.Retract()
                    result = "<.算符."+str(self.line)+"\n"
            elif self.ch == '>':
                self.GetChar()

                if self.ch=='=':
                    result = ">=.算符."+str(self.line)+"\n"
                else:
                    self.Retract()
                    result = ">.算符."+str(self.line)+"\n"
            elif self.ch in self.calsign:
                result = self.ch+".算符."+str(self.line)+"\n"
            elif self.ch in self.rimsign:
                result = self.ch+".界符."+str(self.line)+"\n"
            elif self.ch ==self.end :
                break
            else:
                print("line",self.line,"col",self.col,":error!",self.ch,"is unexpected!")
            f.write(result)
        f.close()
        f = open("id.txt", "w")
        f.write(','.join(lex.id))
        f.close()
        f = open("const.txt", "w")
        f.write(','.join(lex.const))
        f.close()

lex = lexical()
lex.analise()



