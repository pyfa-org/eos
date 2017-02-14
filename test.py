class A:

    def __init__(self, a):
        self.a = a

    def __eq__(self, other):
        if self.a == other.a:
            return True
        else:
            return False


a1 = A(1)
a2 = A(1)
a3 = A(1)

l = [a1, a2]

print(a3 in l)
