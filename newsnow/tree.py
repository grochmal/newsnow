#!/usr/bin/env python3

# Comments on the exercise and pseudo documentation:
#
# Given that no balancing is needed the tree is built by inserting items
# according to the ordering provided by a function.  i.e. the constructor is a
# higher order function as a function need to be provided to it.  Moreover the
# function used to order the elements can be changed anytime, this has no
# visible practical applications but is an interesting API.
#
# The comparison function must abide by the following interface:
#   fun(a, b) equals:
#     -1 if a < b
#      0 if a = b
#      1 if a > b
# As this function will be used to order the keys provided for the tree.
#
# Both the constructor and the insert method accept an arbitrary number of
# arguments.  All these arguments must follow the dictionary interface and
# contain two keys: 'key' and 'val'.  The value under 'key' will be used as a
# key of the value to be inserted in the tree, the value to be inserted being
# the value under 'val'.  i.e. the following results in 6.
#
#   BKTree(lambda x,y: (l>r) - (l<r), {'key':1,'val':6}).get(1)
#
# And is equivalent to:
#
#   BKTree(lambda x,y: (l>r) - (l<r)).insert({'key':1,'val':6}).get(1)
#
# And yeah, it took me *4 hours* to write this implementation.  On the bright
# side i made some tests and a pretty print function.  It could be made better,
# for example, the assumption that there are only 3 elements per node allowed
# me to move some of the insert code into the node (which looks horrible but i
# guess it is not worth spending more time on this).

KEY = 'key'
VAL = 'val'

INDENT_STEP = '    '

# Python 3 has no cmp function (python 2 had it).
# This will is needed as the simplest possible client function used to order
# keys and the way they're placed on the tree.
def cmp(l, r):
    return (l > r) - (l < r)

class TreeLeaf:
    def __init__(self, key, val):
        self.key = key
        self.val = val

# As we are not implementing deletion a node will always hold two or three
# elements.  Therefore we can allow for it to deal with the insertion of an
# element by itself.  This is a rather dirty (and ugly) solution but it works
# within the constraints.
class TreeBranch:
    def __init__(self, left, lkey, centre, rkey, right):
        self.left   = left
        self.lkey   = lkey
        self.centre = centre
        self.rkey   = rkey
        self.right  = right

    def full(self):
        if self.left and self.centre and self.right:
            return True
        return False

    # note that we are comparing the new leaf on the left side of all
    # comparisons
    def insert(self, cmpfun, leaf):
        if 0 >= cmpfun(leaf.key, self.lkey):
            # shift everything to the right
            self.right  = self.centre
            self.rkey   = self.lkey
            self.centre = self.left
            self.lkey   = leaf.key
            self.left   = leaf
        elif 0 >= cmpfun(leaf.key, self.rkey):
            # squeeze new leaf in the middle
            self.right  = self.centre
            self.rkey   = leaf.key
            self.centre = leaf
        else:
            # place the new leaf in the empty (right hand) position
            self.right  = leaf
        return self

    # will be needed if deletion or balancing is to be implemented
    def empty(self):
        pass

class BKTree:
    def __init__(self, cmpfun, *argc):
        # We store the comparison function so we do not need to check its
        # validity on each client call, if the client wants to change the
        # function only then it must be checked (as to not contain rubbish)
        self.tree = None
        self.setcmpfun(cmpfun)
        self.insert(*argc)

    # The client can bypass this at any point, but then
    # it will be the client's fault that we crashed.
    def setcmpfun(self, cmpfun):
        if not callable(cmpfun):
            raise ValueError('{0} must be callable'.format(cmpfun))
        self.cmpfun = cmpfun

    def insert(self, *argc):
        for a in argc:
            if not hasattr(a, 'get'):
                raise ValueError('{0} must behave as a dict'.format(a))
            if None == a.get(KEY, None):
                raise ValueError('No "{0}" attribute in {1}'.format(KEY, a))
            if None == a.get(VAL, None):
                raise ValueError('No "{0}" attribute in {1}'.format(VAL, a))
        # only insert if all arguments are correct
        # so we do not fall into an inconsistent state
        for a in argc:
            leaf = self._get(self.tree, a.get(KEY))
            if None == leaf:  # not here already insert
                self.tree = self._insert_one(self.tree, a.get(KEY), a.get(VAL))
            else:  # already in the tree, update
                leaf.val = a.get(VAL)
        return self

    # This is the actual recursive call into the tree
    def _insert_one(self, tree, key, val):
        if None == tree:  # first insert into this part of the tree
            return TreeLeaf(key, val)
        if isinstance(tree, TreeBranch):
            if tree.full():  # this node is full, go forward
                if 0 >= self.cmpfun(key, tree.lkey):
                    tree.left = self._insert_one(tree.left, key, val)
                    return tree
                elif 0 >= self.cmpfun(key, tree.rkey):
                    tree.centre = self._insert_one(tree.centre, key, val)
                    return tree
                else:
                    tree.right = self._insert_one(tree.right, key, val)
                    return tree
            else:  # node not full, juggle elements
                return tree.insert(self.cmpfun, TreeLeaf(key, val))
        if isinstance(tree, TreeLeaf):
            if 0 >= self.cmpfun(key, tree.key):
                return TreeBranch( TreeLeaf(key, val) , key
                                 , tree               , tree.key
                                 , None
                                 )
            else:
                return TreeBranch( tree               , tree.key
                                 , TreeLeaf(key, val) , key
                                 , None
                                 )

    def get(self, key):
        leaf = self._get(self.tree, key)
        if isinstance(leaf, TreeLeaf):
            return leaf.val
        return None

    # for convenience it returns a leaf, so updating the values in the tree
    # become as simple as getting to the leaf and assigning a new value to it
    def _get(self, tree, key):
        if None == tree:
            return None
        elif isinstance(tree, TreeLeaf):
            if key != tree.key:
                return None
            return tree
        elif isinstance(tree, TreeBranch):
            if 0 >= self.cmpfun(key, tree.lkey):
                return self._get(tree.left, key)
            elif 0 >= self.cmpfun(key, tree.rkey):
                return self._get(tree.centre, key)
            else:
                return self._get(tree.right, key)
        else:
            assert(False)

    def print(self):
        self._print_tree(self.tree, '')

    def _print_tree(self, tree, indent):
        if None == tree:
            print('{0}|-> {1}'.format(indent, None))
        elif isinstance(tree, TreeLeaf):
            print('{0}|-> {1}: {2}'.format(indent, tree.key, tree.val))
        elif isinstance(tree, TreeBranch):
            print('{0}\\branch'.format(indent))
            self._print_tree(tree.left,   indent + INDENT_STEP)
            print('{0}|[key: {1}]'.format(indent + INDENT_STEP, tree.lkey))
            self._print_tree(tree.centre, indent + INDENT_STEP)
            print('{0}|[key: {1}]'.format(indent + INDENT_STEP, tree.rkey))
            self._print_tree(tree.right,  indent + INDENT_STEP)
        else:  # if we got here something very bad happened
            assert(False)

### TESTS ###

# simple unittest for exceptions
def assert_raise(cond, ex):
    try:
        cond()
    except Exception as e:
        if isinstance(e, ex):
            return True
        raise AssertionError
    return True

# cmp
assert( 0 == cmp(1,1))
assert( 1 == cmp(1,0))
assert(-1 == cmp(0,1))
assert_raise(lambda: cmp('a',1), TypeError)

# TreeBranch
assert(TreeBranch(1,1,2,2,3).full())
assert(False == TreeBranch(1,1,2,2,None).full())
assert(TreeBranch(1,1,2,2,None).insert(cmp,TreeLeaf(3,3)).full())

# BKTree __init__
assert_raise(lambda: BKTree(3), ValueError)

# BKTree setcmpfun
tree = BKTree(cmp)
assert_raise(lambda: tree.setcmpfun(3), ValueError)

# BKTree insert
tree = BKTree(cmp)
tree.insert( { 'key' : 1, 'val' : 1 } )
assert_raise(lambda: tree.insert('rubbish'), ValueError)

# BkTree get
tree = BKTree( cmp
             , { 'key' : 1 , 'val' : 1 }
             , { 'key' : 3 , 'val' : 3 }
             , { 'key' : 2 , 'val' : 1 }
             , { 'key' : 7 , 'val' : 1 }
             , { 'key' : 6 , 'val' : 1 }
             , { 'key' : 7 , 'val' : 2 }
             , { 'key' : 0 , 'val' : 2 }
             , { 'key' : 7 , 'val' : 2 }
             )
assert(3 == tree.get(3))
assert(1 == tree.get(6))
assert(2 == tree.get(7))

# reverse of cmp
def recmp(l, r):
    return (l < r) - (l > r)

# change cmp function
tree = BKTree( cmp
             , { 'key' : 1 , 'val' : 1 }
             , { 'key' : 3 , 'val' : 3 }
             , { 'key' : 2 , 'val' : 1 }
             , { 'key' : 6 , 'val' : 1 }
             , { 'key' : 7 , 'val' : 2 }
             )
tree.setcmpfun(recmp)
# this will get inserted on the opposite side of the tree
tree.insert( { 'key' : 7 , 'val' : 3 } )
assert(3 == tree.get(7))
tree.setcmpfun(cmp)
assert(2 == tree.get(7))

### PRESENTATION ###

if '__main__' == __name__:
    tree = BKTree( cmp
                 , { 'key' :  1 , 'val' : 1 }
                 , { 'key' :  3 , 'val' : 3 }
                 , { 'key' :  2 , 'val' : 1 }
                 , { 'key' :  6 , 'val' : 1 }
                 , { 'key' :  7 , 'val' : 2 }
                 , { 'key' : -7 , 'val' : 2 }
                 , { 'key' : -9 , 'val' : 2 }
                 , { 'key' : -1 , 'val' : 4 }
                 , { 'key' :  0 , 'val' : 2 }
                 , { 'key' : 13 , 'val' : 7 }
                 , { 'key' : 11 , 'val' : 2 }
                 , { 'key' :  5 , 'val' : 2 }
                 , { 'key' :  4 , 'val' : 5 }
                 )
    tree.print()

