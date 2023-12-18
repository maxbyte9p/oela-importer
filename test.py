import os
from github import Github, Auth
from github.Organization import Organization
from github.PaginatedList import PaginatedList
import koji
import collect_data

def Github_Authenticate() -> Auth.Token:
    github_token = open(os.environ['HOME'] + "/.github_tokens/openela-import").read().rstrip('\n')
    return Auth.Token(github_token)


def Create_Github_Session(auth: Auth.Token) -> Github:
    return Github(auth=auth)

def Get_Organization(session: Github, org: str = 'openela-main') -> Organization:
    return session.get_organization(org)

def Get_Raw_Repos(org: Organization, visibility: str = 'public') -> PaginatedList:
    return org.get_repos(visibility)

def Generate_Repo_Collection_Map(pl: PaginatedList) -> map:
    return map(
            collect_data.collect,
            pl
    )

def Create_Koji_Session(config_name: str = 'kojidev') -> koji.ClientSession:
    koji_config = koji.read_config(config_name)
    koji_session_opts = koji.grab_session_options(koji_config)
    koji_session = koji.ClientSession(koji_config['server'], koji_session_opts)
    koji_session.gssapi_login()
    koji_session.exclusiveSession()

    return koji_session

def koji_import(
        koji_session: koji.ClientSession,
        repo_data: collect_data.Repo_Data,
        desired_branch: str,
        koji_target: str
) -> int | None:
    if not desired_branch in [b.name for b in repo_data.branches]:
        return None

    return koji_session.build(
            src='git+'+repo_data.clone_url+'#'+desired_branch,
            target=koji_target
    )

def Run() -> None:
    gsession = Create_Github_Session(
            Github_Authenticate()
    )
    repo_data_map = Generate_Repo_Collection_Map(
            Get_Raw_Repos(
                Get_Organization(gsession)
            )
    )

    ksession = Create_Koji_Session()

    oela_import = lambda r: koji_import(ksession, r, 'el-9.3', 'dist-openela9')
    oela_import_feedback = lambda r: print(f"Package: {r.name}, Task ID: {oela_import(r)}")
    for i in repo_data_map:
        oela_import_feedback(i)

