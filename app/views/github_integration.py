from github import Github, GithubException, UnknownObjectException
from flask import current_app

def create_github_repo(project_name, description):
    try:
        github_token = current_app.config['GITHUB_ACCESS_TOKEN']
        g = Github(github_token)
        user = g.get_user()
        repo = user.create_repo(project_name, description=description, private=False)
        
        # 기본 브랜치 생성 (보통 'main')
        try:
            # README.md 파일 생성
            repo.create_file("README.md", 
                             "Initial commit", 
                             f"# {project_name}\n\n{description}", 
                             branch="main")
            current_app.logger.info(f'리포지토리 "{repo.full_name}"가 생성되고 기본 브랜치 "main"이 생성되었습니다.')
        except GithubException as e:
            current_app.logger.error(f'기본 브랜치 생성 중 오류 발생: {e.status} {e.data}')
            # 리포지토리는 생성되었지만 기본 브랜치 생성에 실패한 경우
            return True, repo.full_name, "리포지토리는 생성되었지만 기본 브랜치 생성에 실패했습니다."

        return True, repo.full_name, "리포지토리가 성공적으로 생성되었습니다."
    except GithubException as e:
        current_app.logger.error(f'GitHub 리포지토리 생성 중 오류 발생: {e.status} {e.data}')
        return False, None, f"GitHub 리포지토리 생성 실패: {e.data.get('message', str(e))}"
    except Exception as e:
        current_app.logger.error(f'예상치 못한 오류 발생: {str(e)}')
        return False, None, f"예상치 못한 오류 발생: {str(e)}"

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
    except GithubException as e:
        if e.status == 404 and "This repository is empty" in str(e.data):
            current_app.logger.info(f'리포지토리가 비어 있습니다: {repo.full_name}')
            return []
        else:
            current_app.logger.error(f'파일 목록을 가져오는 중 GitHub 오류 발생: {e.status} {e.data}')
            raise
    except Exception as e:
        current_app.logger.error(f'파일 목록을 가져오는 중 예상치 못한 오류 발생: {str(e)}')
        raise


def create_github_file(repo, file_name, code_content, branch_name, commit_message):
    try:
        current_app.logger.info(f'파일 생성 시도: 리포지토리 = {repo.full_name}, 파일 = {file_name}, 브랜치 = {branch_name}')
        
        # 파일을 생성합니다
        result = repo.create_file(file_name, commit_message, code_content, branch=branch_name)
        current_app.logger.info(f'파일 생성 결과: {result}')
        return True, f'새 파일 "{file_name}"이 브랜치 "{branch_name}"에 생성되었습니다.'
    except GithubException as e:
        error_message = f'GitHub 작업 중 오류 발생: {e.status} {e.data.get("message", str(e))}'
        current_app.logger.error(error_message)
        return False, error_message
    except Exception as e:
        error_message = f'예상치 못한 오류 발생: {str(e)}'
        current_app.logger.error(error_message)
        return False, error_message
    

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