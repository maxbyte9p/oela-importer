from typing import NamedTuple
from koji import ClientSession
from collect_data import Repo_Data

class Import_Target(NamedTuple):
    name: str
    src: str
    target: str

def Create_Import_Target(
        rd: Repo_Data,
        db: str,
        t: str
) -> Import_Target:
    if not db in [b.name for b in rd.branches]:
        return None

    return Import_Target(
            name=rd.name,
            src='git+'+rd.clone_url+'#'+db,
            target=t
    )

def Koji_Import(session: ClientSession, it: Import_Target, owner: str) -> int:
    session.packageListAdd(it.target, it.name, owner)
    return session.build(it.src, it.target)


