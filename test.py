import os
from github import Github, Auth
import koji
import collect_data

github_token = open(os.environ['HOME'] + "/.github_tokens/openela-import").read().rstrip('\n')
github_auth = Auth.Token(github_token)
github_session = Github(auth=github_auth)

openela_main = github_session.get_organization('openela-main')
openela_main_repos = openela_main.get_repos('public')
openela_main_repos_data = collect_data.applied_func_iter(
        openela_main_repos,
        collect_data.collect_repo_data
)

koji_config = koji.read_config('kojidev')
koji_session_opts = koji.grab_session_options(koji_config)
koji_session = koji.ClientSession(koji_config['server'], koji_session_opts)
koji_session.gssapi_login()
koji_session.exclusiveSession()

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

oela_import = lambda r: koji_import(koji_session, r, 'el-9.3', 'dist-openela9')

oela_import_feedback = lambda r: print(f"Package: {r.name}, Task ID: {oela_import(r)}")

run = lambda: [i for i in map(oela_import_feedback, openela_main_repos_data)]
run()

