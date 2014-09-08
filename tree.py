__author__ = 'Francesco'


class Node:
    def __init__(self, content, parent=None, left=None, right=None):
        self.content = content
        self.left = left
        self.right = right
        self.parent = parent

    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.right = right
