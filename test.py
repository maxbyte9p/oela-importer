import os
from itertools import starmap
from github import Github, Auth
from github.Organization import Organization
from github.PaginatedList import PaginatedList
import koji
import importer
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

def Generate_Import_Target_Map(rdm: map, db: str, t: str) -> starmap:
    return filter(
            None,
            starmap(
                importer.Create_Import_Target,
                (tuple([rd, db, t]) for rd in rdm)
            )
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

    import_target_map = Generate_Import_Target_Map(
            repo_data_map,
            'el-9.3',
            'dist-openela9'
    )

    ksession = Create_Koji_Session()
    for i in import_target_map:
        importer.Koji_Import(ksession, i)
        print(f"Imported: {i}")


Run()
