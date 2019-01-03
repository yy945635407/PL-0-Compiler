class PcodeTable:
    # 假象目标机代码串
    def __init__(self):
        self.i = 0 #代码指针
        self.Codes = []

    def gen(self,f,l,a):
        code = Pcode()
        code.set(f,l,a)
        self.Codes.append(code)
        self.i += 1

    def show(self):
        for code in self.Codes:
            print("("+str(self.Codes.index(code))+")",end=" ")
            print(code)

    def backPatch(self, i, adr):#回填第i条指令的地址
        self.Codes[i].A = adr

    def interpreter(self, procs, debug=False):#解释执行所有代码 ,procs为函数名字及其参数个数
        Stack = []
        maxStackSize = 100
        for i in range(0,maxStackSize):
            Stack.append(0)
        oprs = ['+','-','*','/','ha','haha','==','!=','<','>=','>','<='] #用于对应两目操作
        preCode = None
        code = self.Codes[0]
        sp = 0 #栈顶指针
        bp = 0 #基地址寄存器
        while True:
            jmp = False #是否跳转
            if code.F == "INT":# 在栈中开辟大小为A的数据区
                if bp == 0:#对最外层增加display
                    Stack[bp+2] = [0]
                sp += code.A

            elif code.F == "CAL":# 调用过程
                returnAdr = self.Codes.index(code)+1 #当前指令的下一条指令为返回地址
                oldBp = bp #调用者的活动记录首地址
                paramNum = 0 #参数个数
                params = [] #参数值
                for item in procs:
                    if item[2] == code.A:
                        paramNum = item[1]

                display = [sp-paramNum]
                for item in Stack[bp+2]:
                    display.append(item)
                # 传参
                t = 0
                while t<paramNum:#暂存参数
                    params.append(Stack[sp-paramNum+t])
                    t += 1
                sp = sp - paramNum
                t = 0
                for param in params: #将参数存入数据区
                    Stack[sp+4+t] = param
                    t += 1
                bp = sp
                preCode = code
                code = self.Codes[code.A]

                jmp = True

                Stack[bp] = oldBp
                Stack[bp+1] = returnAdr
                Stack[bp+2] = display
                Stack[bp+3] = paramNum


            elif code.F == "LIT":# 将值为code.A的常量值送到栈顶
                Stack[sp] = code.A
                sp += 1

            elif code.F == "LOD":# 将相对位置为code.A变量送到栈顶
                try:
                    base = Stack[bp+2][code.L] #基地址
                except:
                    base = bp
                Stack[sp] = Stack[base+code.A]
                sp += 1

            elif code.F == "STO":# 将栈顶内容送入相对位置为code.A的位置
                try:
                    base = Stack[bp+2][code.L]
                except:
                    base = bp
                Stack[base+code.A] = Stack[sp]

            elif code.F == "JMP":# 无条件转移到地址为code.A的指令
                preCode = code
                code = self.Codes[code.A]
                jmp = True

            elif code.F == "JPC":# 条件转移，当栈顶的值为0时，转到地址为code.A的指令
                if Stack[sp] == False:#为0跳转
                    preCode = code
                    code = self.Codes[code.A]
                    jmp = True
                #为1顺序执行

            elif code.F == "RED":# 将终端输入存入相对地址为code.A的变量
                print("input:",end="")
                get = eval(input())
                try:
                    base = Stack[bp+2][code.L]
                except:
                    base = bp
                Stack[base+code.A] = get

            elif code.F == "WRT":# 将栈顶值输出到屏幕上
                print("output:", end="")
                if preCode.F == "LOD" or preCode.F == "LIT":
                    print(Stack[sp-1], end="")
                else:
                    print(Stack[sp], end="")

            else: # OPR 操作
                if code.A == 0:# 返回调用点
                    sp = bp
                    preCode = code
                    code = self.Codes[Stack[bp + 1]]
                    if code == self.Codes[0]:#最外层过程返回，结束运行
                        return
                    jmp = True
                    bp = Stack[bp]

                elif code.A == 1:# -栈顶
                    Stack[sp] = -Stack[sp]

                elif code.A == 6:# 判断栈顶奇偶
                    Stack[sp] =  Stack[sp]%2==0 #偶为True，奇为False

                elif code.A == 15:#输出屏幕换行
                    print()

                else:
                    Stack[sp - 2] = eval(str(Stack[sp - 2]) + oprs[code.A-2] + str(Stack[sp - 1])) #2对应+，3对应-以此类推
                    sp -= 2
            if jmp == False:
                # 继续取下一条指令
                preCode = code
                code = self.Codes[self.Codes.index(code) + 1]
            if debug == True:
                print(code)
                print(Stack)
                input()

class Pcode:
    # 假象目标机代码
    def __init__(self):
        self.F = ""
        self.L = 0
        self.A = 0

    def set(self,f,l,a):
        self.F = f
        self.L = l
        self.A = a

    def __str__(self):
        str = "{}\t{}\t{}"
        return str.format(self.F, self.L, self.A)
