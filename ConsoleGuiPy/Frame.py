from Element import ELEMENT, UTILITY


class FRAME(ELEMENT):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.Util = UTILITY()
        self.name = ""
        self.namecolor = "\x1b[0m"
        self.nameindent = 5
        self.current.height = height
        self.current.width = width
        self.current.vertical_position = y
        self.current.horizontal_position = x

        self.previous.height = height
        self.previous.width = width
        self.previous.vertical_position = y
        self.previous.horizontal_position = x
    

    def __del__(self):
        self.erase()
    
    def set_name(self, string, indent = 6):
        self.name = string
        self.nameindent = indent
    
    def hide_name(self):
        self.name = ""

    def set_namecolor(self, r, g, b):
        self.namecolor = f'\x1b[38;2;{r};{g};{b}m'

    def render(self):

        X = self.current.horizontal_position
        Y = self.current.vertical_position
        Height = self.current.height
        Width = self.current.width
        
        print(self.current.color)
        self.Util.box(X, Y, Width, Height)
        self.resetColor()
        
         #Print the name of frame
        if(self.name != ""):

            print(self.namecolor)
            self.Util.cursor(X + self.nameindent, Y) 
            print(self.name)
            self.resetColor()
        
        self.previous << self.current
    
    def erase(self):
        X = self.previous.horizontal_position
        Y = self.previous.vertical_position
        Height = self.previous.height
        Width = self.previous.width
        
        self.Util.erasebox(X, Y, Width, Height)

