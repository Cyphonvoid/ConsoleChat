class UTILITY:

    def __init__(self):
        
        pass

    def __del__(self):
        pass

    def Vline(self, x, y, len, char):
        line = ""
        for i in range(y, y+len):
            line = line + self.cursor(x, i) + char
        
        print(line)
        return line
        

    def Hline(self, x, y, len, char):
        line = self.cursor(x, y) + (char * len)
        print(line)
        return line
    
    def point(self, x, y, char):
        p = self.cursor(x, y) + char
        print(p)
        return p
    
    def box(self, x, y, width, height):
        top_left = '┏'
        top_right = '┓'
        bottom_left = '┗'
        bottom_right = '┛'
        width = width * 2

        self.Vline(x, y, height, '┃')
        self.Vline(x+width, y, height, '┃')
        self.Hline(x, y, width, '━')
        self.Hline(x, y+height, width, '━')

        self.point(x, y, top_left)
        self.point(x+width, y, top_right)
        self.point(x, y+height, bottom_left)
        self.point(x + width, y + height, bottom_right)
    
    def erasebox(self, x, y, width, height):
        width = width * 2
        char = ' '
        self.Vline(x, y, height, char)
        self.Vline(x+width, y, height, char)
        self.Hline(x, y, width, char)
        self.Hline(x, y+height, width+1, char)
    
    def eraseArea(self, x, y, width, height):

        char = ' '
        
        for i in range(y, y+height):
            self.Hline(x, i, width, char)
   
    def clear(self):
        print("\033c")

    def cursor(self, X, Y):
        pos = "\033[" + str(Y) + ";" + str(X) + "H"
        print(pos, end="")
        return pos

class ATTRIBUTES:

    def __init__(self, horizontal_position=0, vertical_position=0, height=0, width=0, color="\033[0m"):
        self.horizontal_position = horizontal_position
        self.vertical_position = vertical_position
        self.height = height
        self.width = width
        self.color = color

    def __lshift__(self, other):
        self.vertical_position = other.vertical_position
        self.horizontal_position = other.horizontal_position
        self.width = other.width
        self.height = other.height

class ELEMENT:
   

    def __init__(self):
        self.previous = ATTRIBUTES()
        self.current = ATTRIBUTES()

    def getX(self):
        return self.current.horizontal_position

    def getY(self):
        return self.current.vertical_position
    
    def getW(self):
        return self.current.width*2
    
    def getH(self):
        return self.current.height
    
    def set_position(self, x, y):
        self.current.vertical_position = y
        self.current.horizontal_position = x
    
    def set_height(self, h):
        self.current.height = h

    def set_width(self, w):
        self.current.width = w
    
    def setRGB(self, r, g, b):
        self.current.color = f'\x1b[38;2;{r};{g};{b}m'

    def resetColor(self):
        print('\033[0m')

    def StateChange(self):
        pass

    def erase(self):
        pass

    def render(self):
        pass

    def draw(self):
        self.erase()
        self.render()