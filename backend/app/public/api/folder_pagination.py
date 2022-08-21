from dataclasses import dataclass


@dataclass
class PaginationParams:
    after: int
    limit: int


@dataclass
class PaginationLinks:
    next: str = ""


def get_pagination_links(
    api_path: str,
    req_pagination_params: PaginationParams,
    next: int,
):
    links = PaginationLinks()
    if next != 0:
        links.next = pagination_link(
            api_path,
            next,
            req_pagination_params.limit,
        )
    return links


def pagination_link(
    api_path: str,
    after: int,
    limit: int,
):
    link = api_path + "?"
    if after != 0:
        link += f"after={after}&"
    if limit != 0:
        link += f"limit={limit}&"

    return link.rstrip("&")
