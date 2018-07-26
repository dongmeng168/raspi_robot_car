def catch(origin_func):
    def wrapper(self, *args, **kwargs):
        print("catch start")
        # print(self.name)
        origin_func(self, *args, **kwargs)
        print(self.name)
        print("catch end")
    return wrapper




class Decorator(object):
    def __init__(self, f):
        self.f = f
    def __call__(self):
        print("decorator start")

        self.f()
        print(self.name)        
        print("decorator end")

class MyShow(object):
    @catch
    def showName(self):
        self.name = "dongmeng"
        print("show name")

ms1 = MyShow()
ms1.showName()