from github import Github, GithubException
from flask import current_app

def get_github_repo(project):
    github_token = current_app.config['GITHUB_ACCESS_TOKEN']
    g = Github(github_token)
    return g.get_repo(project.github_repo)

def get_branches_internal(repo):
    return [branch.name for branch in repo.get_branches()]

def get_files_internal(repo, branch):
    try:
        files = []
        contents = repo.get_contents("", ref=branch)
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=branch))
            else:
                files.append({"path": file_content.path, "type": file_content.type})
        return files
    except Exception as e:
        current_app.logger.error(f'파일 목록을 가져오는 중 오류 발생: {str(e)}')
        return []

def create_github_file(repo, file_name, code_content, branch_name, commit_message):
    try:
        # 브랜치 확인 및 생성
        try:
            repo.get_branch(branch_name)
        except GithubException as e:
            if e.status == 404:
                default_branch = repo.get_branch(repo.default_branch)
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha)
                return True, f'새로운 브랜치 "{branch_name}"가 생성되었습니다.'
            else:
                raise

        # 새 파일 생성
        repo.create_file(file_name, commit_message, code_content, branch=branch_name)
        return True, f'새 파일 "{file_name}"이 생성되었습니다.'
    except GithubException as e:
        return False, f'GitHub 작업 중 오류가 발생했습니다: {e.data.get("message", str(e))}'
    except Exception as e:
        return False, f'예상치 못한 오류가 발생했습니다: {str(e)}'

def update_github_file(repo, file_path, content, branch_name, commit_message):
    try:
        contents = repo.get_contents(file_path, ref=branch_name)
        repo.update_file(contents.path, commit_message, content, contents.sha, branch=branch_name)
        return True, f'파일 "{file_path}"이 업데이트되었습니다.'
    except GithubException as e:
        return False, f'GitHub 작업 중 오류가 발생했습니다: {e.data.get("message", str(e))}'
    except Exception as e:
        return False, f'예상치 못한 오류가 발생했습니다: {str(e)}'

def get_file_content(repo, file_path, branch_name):
    try:
        content = repo.get_contents(file_path, ref=branch_name)
        return True, content.decoded_content.decode('utf-8')
    except Exception as e:
        return False, str(e)