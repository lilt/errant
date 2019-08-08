class Node:
    """
    A class to represent the nodes in SCRDR tree
    """

    def __init__(self, condition, conclusion, father = None, exceptChild = None, elseChild = None, cornerstoneCases = [], depth = 0):
        self.condition = condition
        self.conclusion = conclusion
        self.exceptChild = exceptChild
        self.elseChild = elseChild
        self.cornerstoneCases = cornerstoneCases
        self.father = father
        self.depth = depth

    def satisfied(self, local_object):
        return eval(self.condition)

    def execute_conclusion(self, local_object):
        exec(self.conclusion)

    def append_cornerstone_case(self, local_object):
        self.cornerstoneCases.append(local_object)

    def check(self, local_object):
        if self.satisfied(local_object):
            self.execute_conclusion(local_object)
            if self.exceptChild is not None:
                self.exceptChild.check(local_object)
        else:
            if self.elseChild is not None:
                self.elseChild.check(local_object)

    def check_depth(self, local_object, length):
        if self.depth <= length:
            if self.satisfied(local_object):
                self.execute_conclusion(local_object)
                if self.exceptChild is not None:
                    self.exceptChild.check_depth(local_object, length)
            else:
                if self.elseChild is not None:
                    self.elseChild.check_depth(local_object, length)

    def find_real_father(self):
        node = self
        father_node = node.father
        while True and father_node is not None:
            if father_node.exceptChild == node:
                break
            node = father_node
            father_node = node.father
        return father_node

    def add_else_child(self, node):
        father_node = self.find_real_father()
        for local_object in father_node.cornerstoneCases:
            if node.satisfied(local_object):
                print("The new rule fires the cornerstone cases of its father node!!!")
                self.find_real_father().cornerstoneCases.remove(local_object)
        self.elseChild = node
        return True

    def add_except_child(self, node):
        for local_object in self.cornerstoneCases:
            if node.satisfied(local_object):
                print("The new rule fires the cornerstone cases of its father node!!!")
                self.cornerstoneCases.remove(local_object)
        self.exceptChild = node
        return True

    def write_to_file_with_seen_cases(self, out, depth):
        space = tab_str(depth)
        out.write(space + self.condition + " : " + self.conclusion + "\n")
        for case in self.cornerstoneCases:
            out.write(" " + space + "cc: " + case.toStr() + "\n")
        if self.exceptChild is not None:
            self.exceptChild.write_to_file(out, depth + 1)
        if self.elseChild is not None:
            self.elseChild.write_to_file(out, depth)

    def write_to_file(self, out, depth):
        space = tab_str(depth)
        out.write(space + self.condition + " : " + self.conclusion + "\n")
        if self.exceptChild is not None:
            self.exceptChild.write_to_file(out, depth + 1)
        if self.elseChild is not None:
            self.elseChild.write_to_file(out, depth)


def tab_str(length):
    return "".join(["\t"] * length)
