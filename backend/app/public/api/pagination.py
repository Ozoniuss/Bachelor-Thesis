from dataclasses import dataclass


@dataclass
class PaginationParams:
    after: str
    before: str
    limit: str


@dataclass
class PaginationLinks:
    prev: str = ""
    next: str = ""


def get_pagination_links(
    api_path: str,
    # pagination params that were sent in the request
    req_pagination_params: PaginationParams,
    next: str,
    prev: str,
    filters: dict = None,
):
    links = PaginationLinks()
    if next != "":
        links.next = pagination_link(
            api_path,
            req_pagination_params.before,
            next,
            req_pagination_params.limit,
            filters,
        )
    if prev != "":
        links.prev = pagination_link(
            api_path,
            prev,
            req_pagination_params.after,
            req_pagination_params.limit,
            filters,
        )
    return links


def pagination_link(
    api_path: str,
    before: str,
    after: str,
    limit: int,
    filters: dict = None,
):
    link = api_path + "?"
    if before != "":
        link += f"before={before}&"
    if after != "":
        link += f"after={after}&"
    if limit != 0:
        link += f"limit={limit}&"

    if filters != None:
        for key, val in filters.items():
            link += f"{key}={val}&"

    return link.rstrip("&")
