# -*- coding: utf-8 -*-

from LOTlib.Node import Node

class TerminalNode(Node):
    def __init__(self, parent, string):
        super(TerminalNode, self).__init__(parent)
        self.string = string

    def __str__(self):
        return self.string

    @property
    def pystring(self):
        return "'"+self.string+"'"

    @property
    def log_prob(self):
        return 0.

    @property
    def size(self):
        return 1

    def __iter__(self):
        yield self

    def debugstring(self, depth=0):
        return '|'*depth + self.string
