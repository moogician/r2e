from pydantic import BaseModel
from pathlib import Path


class Identifier(BaseModel):
    identifier: str

    @classmethod
    def from_relative_path(cls, relative_path: Path) -> "Identifier":
        """
        Create an identifier from a path relative to the repo
        """
        path_str = relative_path.name
        if relative_path.name.endswith(".py"):
            path_str = relative_path.name[:-3]
        return cls(identifier=path_str.replace("/", "."))

    @classmethod
    def from_absolute_path_repo_path(
        cls, absolute_path: Path, repo_path: Path
    ) -> "Identifier":
        """
        Create an identifier from a absolute path and the repo path
        """
        return cls.from_relative_path(repo_path.relative_to(absolute_path))

    def __str__(self):
        return self.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if isinstance(other, Identifier):
            return self.identifier == other.identifier
        return False
