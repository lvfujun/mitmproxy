import sortedcontainers
import itertools

incId = itertools.count()


def getIncId():
    global incId
    return next(incId)

def resetId():
    global incId
    incId=itertools.count()


class _SortedListWithKey(sortedcontainers.SortedListWithKey):
    pass
