from sqlalchemy import desc, Column
from flask_sqlalchemy import BaseQuery


class PaginationParametersException(Exception):
    pass


"""
This functions are used for cursor pagination.
TODO: documentation
"""

ASC = "asc"
DESC = "desc"


def paginate(
    query: BaseQuery,
    cursorColumn: Column,
    limit: int,
    before: str,
    after: str,
    order: str,
):
    """
    This function applies the necessary clauses to generate a paginated list of
    elements.
    """

    if order not in [ASC, DESC]:
        raise PaginationParametersException('Order must be "asc" or "desc"')

    if order == "desc":
        tmp = after
        after = before
        before = tmp

        query = query.order_by(desc(cursorColumn))

    else:
        query = query.order_by(cursorColumn)

    if after != "":
        query = query.filter(after <= cursorColumn)

    if before != "":
        query = query.filter(before >= cursorColumn)

    if limit > 0:
        query = query.limit(limit)

    return query


def List(
    query: BaseQuery,
    limit: int,
    cursorColumn: Column,
    retrieveCursor,
    before: str,
    after: str,
    order: int,
):

    prev = ""
    next = ""

    reversed = False

    # reverse the requests, elemen
    if after == "" and before != "":
        tmp = after
        after = before
        before = tmp

        order = reverseOrder(order)

        reversed = True

    if limit <= 0:
        limit = 0
    else:
        if after != "":
            limit += 1

    elements = paginate(query, cursorColumn, limit, before, after, order).all()

    if len(elements) > 0:
        if after != "":
            prev = retrieveCursor(elements[0])

        if len(elements) == limit:
            next = retrieveCursor(elements[len(elements) - 1])

    if reversed:
        l = len(elements)

        if limit > 0 and len(elements) == limit:
            l -= 1

        tmp = []
        for i in range(l - 1, -1, -1):
            tmp.append(elements[i])
        elements = tmp

        tmp = prev
        prev = next
        next = tmp

    else:
        if after != "" and len(elements) > 0:
            elements = elements[1:]

    return elements, prev, next


def reverseOrder(order):
    if order == ASC:
        return DESC
    else:
        return ASC
