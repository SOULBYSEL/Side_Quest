from tkinter import *

class Main:
    def __init__ (self,root):
        self.root = root
        self.root.title("Side Quest")
        self.root.geometry("2222x2222")

if __name__ == '__main__':
    root = Tk()
    obj = Main(root)
    root.mainloop()
