import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from r2e.paths import GRAPHS_DIR
from r2e.models.callgraph import CallGraph


class Repo(BaseModel):
    repo_org: str
    repo_name: str
    repo_path: Path

    _cached_callgraph: Optional[CallGraph] = None

    @property
    def callgraph_path(self) -> str:
        return os.path.join(GRAPHS_DIR, self.repo_id + "_cgraph.json")

    @classmethod
    def from_file_path(cls, file_path: Path | str) -> "Repo":
        repo_path = Path(file_path)
        try:
            repo_org, repo_name = repo_path.name.split("___")
        except:
            repo_org = repo_name = repo_path.name

        return cls(
            repo_org=repo_org,
            repo_name=repo_name,
            repo_path=repo_path,
        )

    @property
    def repo_id(self) -> str:
        return self.repo_path.name

    @property
    def callgraph(self) -> CallGraph:
        if self._cached_callgraph is None:
            self._cached_callgraph = CallGraph.from_json(self.callgraph_path)
        return self._cached_callgraph

    def __hash__(self) -> int:
        return hash(self.repo_id)

    def list_repo_files(self) -> list[Path]:
        return list(map(lambda x: x.relative_to(self.repo_path), 
                        filter(lambda x: x.is_file(), self.repo_path.glob('*'))))

    @property
    def execution_repo_data(self) -> dict[str, str]:
        return {
            "repo_id": self.repo_id,
            "repo_path": self.repo_id,
        }
