from Element import ELEMENT, UTILITY
import re
class TEXTBOX(ELEMENT):

    def __init__(self, x, y, w, h, type = "output"):
        super().__init__()
        self.content = ""
        self.Util = UTILITY()
        self.boxtype = type
        if(type != "output" and type != "input"):
            self.boxtype = "output"

        self.current.horizontal_position = x
        self.current.vertical_position = y
        self.current.height = h
        self.current.width = w
        
        self.previous << self.current
    def __del__(self):
        self.erase()

    
    def write(self, string):
        self.content += string
   
    
    def erase(self):
        X = self.previous.horizontal_position
        Y = self.previous.vertical_position
        H = self.previous.height
        W = self.previous.width
        self.Util.eraseArea(X, Y, W, H)

   
   
    def SetLine(self, x, y, text):
        line = self.Util.cursor(x, y) + text
        return line
    
    def extract_last_position(self, string):
        pattern = r'\x1B\[(\d+);(\d+)H'
        matches = re.finditer(pattern, string)
        last_position = None

        for match in matches:
            row = int(match.group(1))
            column = int(match.group(2))
            last_position = (row, column)

        return last_position

    def discount_ANSI(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def print(self):
        print("previous= ", self.previous.horizontal_position, self.previous.vertical_position)
        print("\ncurrent= ", self.current.horizontal_position, self.current.vertical_position)
    

    def render(self):
        
        #len() doesn't work properly
        c = self.content.count("\n")
        length = len(self.content) + c
        X = self.current.horizontal_position
        Y = self.current.vertical_position
        spos = 0
        epos = 0
        POS = 0
        content = ""
        temp = ""
        var = ""
        self.previous << self.current
        if(length <= self.current.width):
            epos = length

        else:
            epos = self.current.width

         #We're looking for new line characters, based on where they're present we are exractring substring sections and combining them with position to display
        for i in range(0, self.current.height):
            
            #Find the newline character get the position
            POS = self.content.find("\n", spos)
            
            #Check if the substring with newline character is within width
            if((POS - spos) < self.current.width and POS > -1):
                
                #Get that much string with postion and store it
                content += self.SetLine(X, Y, self.content[spos:POS])
                
                #Increment position so we can look at section right after newline char
                spos = POS + 1
                
            elif((POS - spos) >= self.current.width or POS  == -1):
                
                #If the substring doesn't contain newline char that means we can display substring of length of width in a line
                content += self.SetLine(X, Y, self.content[spos:epos])    
                spos = epos
            
            
            #Calculate this to know the value of epos because, if the total remaining content is less than width that means it only needs one mmore line
            #In that case epos will be equal to last index
            remain = length - spos  
            if(remain == 0):
                pass

            elif(remain > self.current.width):
                epos = spos + self.current.width

            elif(remain < self.current.width):
                epos = length
        
            
            Y += 1 
        print(content)
    

    def clear(self):
        self.content = ""
    
    def input_render(self):
        X = self.current.horizontal_position
        Y = self.current.vertical_position

        self.Util.cursor(X, Y)
        print(self.content, end="")
        inp = input()

        self.previous << self.current
        return inp
        
    def draw(self):
        self.erase()
        if(self.boxtype == "output"):
          self.render()

        elif(self.boxtype == "input"):
            return self.input_render()

