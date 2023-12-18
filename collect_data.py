from typing import NamedTuple, TypeAlias
from typing import Union, TypeVar
from collections.abc import Iterable, Iterator, Callable
from functools import wraps
from github.Repository import Repository
from github.Branch import Branch
from github.Tag import Tag

class Branch_Data(NamedTuple):
    """Collected metadata from a Github repository branch"""
    name: str
    commit: str

class Tag_Data(NamedTuple):
    """Collected metadata from a Github repository tag"""
    name: str
    commit: str

class Repo_Data(NamedTuple):
    """Collected metadata from a Github repository"""
    name: str
    clone_url: str
    ssh_url: str
    branches: tuple[Branch_Data]
    tags: tuple[Tag_Data]

Raw: TypeAlias = Union[Repository, Branch, Tag]
RawT = TypeVar("RawT", bound=Raw)
Data: TypeAlias = Union[Repo_Data, Branch_Data, Tag_Data]
DataT = TypeVar("DataT", bound=Data)

def log_collection(
        function: Callable[[RawT], DataT]
) -> Callable[[RawT], DataT]:
    @wraps(function)
    def wrapper(raw: RawT) -> DataT:
        rv = function(raw)
        if isinstance(rv, Repo_Data):
            print(f"Collected Repository: {rv.name}")
        elif isinstance(rv, Branch_Data):
            print(f"Collected Branch: {rv.name}")
        elif isinstance(rv, Tag_Data):
            print(f"Collected Tag: {rv.name}")
        return rv

    return wrapper

def collect(raw: RawT) -> DataT:
    if isinstance(raw, Repository):
        return collect_repo_data(raw)
    elif isinstance(raw, Branch):
        return collect_branch_data(raw)
    elif isinstance(raw, Tag):
        return collect_tag_data(raw)

@log_collection
def collect_repo_data(repo: Repository) -> Repo_Data:
    return Repo_Data(
            name=repo.name,
            clone_url=repo.clone_url,
            ssh_url=repo.ssh_url,
            branches=tuple(
                map(
                    collect,
                    repo.get_branches()
                )
            ),
            tags=tuple(
                map(
                    collect,
                    repo.get_tags()
                )
            )
    )

@log_collection
def collect_branch_data(branch: Branch) -> Branch_Data:
    return Branch_Data(
            name=branch.name,
            commit=branch.commit.sha
    )

@log_collection
def collect_tag_data(tag: Tag) -> Tag_Data:
    return Tag_Data(
            name=tag.name,
            commit=tag.commit.sha
    )





