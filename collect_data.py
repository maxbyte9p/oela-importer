from typing import NamedTuple, TypeAlias
from collections.abc import Iterable, Iterator, Callable
from github import Repository, Branch, Tag

class Branch_Data(NamedTuple):
    """Collected metadata from a Github repository branch"""
    name: str
    commit: str

Tag_Data: TypeAlias = Branch_Data

class Repo_Data(NamedTuple):
    """Collected metadata from a Github repository"""
    name: str
    clone_url: str
    ssh_url: str
    branches: tuple[Branch_Data]
    tags: tuple[Tag_Data]

def applied_func_iter(iterable: Iterable, func: Callable[[any], any]) -> Iterator[any]:
    return ( func(i) for i in iterable ) 

def collect_repo_data(repo: Repository) -> Repo_Data:
    return Repo_Data(
            name=repo.name,
            clone_url=repo.clone_url,
            ssh_url=repo.ssh_url,
            branches=tuple(
                applied_func_iter(
                    iter(repo.get_branches()),
                    collect_branch_data
                )
            ),
            tags=tuple(
                applied_func_iter(
                    iter(repo.get_tags()),
                    collect_tag_data
                )
            )
    )

def collect_branch_data(branch: Branch) -> Branch_Data:
    return Branch_Data(
            name=branch.name,
            commit=branch.commit.sha
    )

def collect_tag_data(tag: Tag) -> Tag_Data:
    return Tag_Data(
            name=tag.name,
            commit=tag.commit.sha
    )
