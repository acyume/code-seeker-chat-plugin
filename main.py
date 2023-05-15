import asyncio
import requests
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

GITHUB_TOKEN = None # add token to increase rate limit
README_MAX_LENGTH = 2048


class Repository(BaseModel):
    name: str
    description: Optional[str]
    url: str
    homepage: Optional[str]
    topics: List[str]
    language: Optional[str]
    license: Optional[str]
    stargazers_count: int
    forks_count: int
    fork: bool
    readme_content: Optional[str]
    created_at: str
    updated_at: str
    pushed_at: str


class SearchResult(BaseModel):
    total_count: int
    items: List[Repository]


app = FastAPI(title='CodeSeeker', version='1.0.0')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN is not None else {}


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def get_plugin_manifest():
    return FileResponse("ai-plugin.json", media_type="application/json")


@app.get("/logo.png", include_in_schema=False)
async def get_logo_image():
    return FileResponse("logo.png", media_type="image/png")


async def get_readme_content(repo):
    print(get_headers())
    readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
    response = requests.get(readme_url, headers={"Accept": "application/vnd.github.VERSION.raw", **get_headers()})

    if response.status_code != 200:
        return None

    readme_content = response.text
    max_length = README_MAX_LENGTH
    if len(readme_content) > max_length:
        last_newline_pos = readme_content.rfind('\n', 0, max_length)
        if last_newline_pos != -1:
            readme_content = readme_content[:last_newline_pos] + "\n... (truncated)"
        else:
            readme_content = readme_content[:max_length] + "... (truncated)"

    return readme_content


async def fetch_readme_and_attach(repo):
    license = repo.get('license')
    if license is not None:
        license = license.get('name')
    return {
        'name': repo['full_name'],
        'description': repo['description'],
        'url': repo['html_url'],
        'homepage': repo['homepage'],
        'topics': repo['topics'],
        'language': repo['language'],
        'license': license,
        'stargazers_count': repo['stargazers_count'],
        'forks_count': repo['forks_count'],
        'fork': repo['fork'],
        'readme_content': await get_readme_content(repo),
        'created_at': repo['created_at'],
        'updated_at': repo['updated_at'],
        'pushed_at': repo['pushed_at'],
    }


@app.get(
    "/search",
    summary="Search relevant GitHub projects based on user queries",
    description="When a user seeks coding advice or shares a development idea, " +
                "use their keywords as the 'query' to search for GitHub projects. " +
                "Analyze and present the returned GitHub project details to inspire and guide the user's project.",
    response_model=SearchResult,
)
async def search_projects(query: str, limit: int=3):
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="GitHub API request failed")

    search_results = response.json()
    repositories = search_results["items"]

    repositories = repositories[:limit]

    tasks = [fetch_readme_and_attach(repo) for repo in repositories]
    updated_repositories = await asyncio.gather(*tasks)

    return {'total_count': search_results['total_count'], 'items': updated_repositories}