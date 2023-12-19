from typing import NamedTuple
from koji import ClientSession
from collect_data import Repo_Data

class Import_Target(NamedTuple):
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
            src='git+'+rd.clone_url+'#'+db,
            target=t
    )

def Koji_Import(session: ClientSession, it: Import_Target) -> int:
    return session.build(*it)


