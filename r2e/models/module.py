from pathlib import Path
from enum import Enum
from pydantic import BaseModel

from r2e.models.repo import Repo
from r2e.models.identifier import Identifier


class ModuleTypeEnum(str, Enum):
    FILE = "file"
    PACKAGE = "package"


class Module(BaseModel):
    module_id: Identifier
    module_type: ModuleTypeEnum = ModuleTypeEnum.FILE
    repo: Repo

    # TODO: maybe don't use . representation for modules/ids
    
    def is_pkg(self) -> bool:
        return self.module_type == ModuleTypeEnum.PACKAGE

    @property
    def local_path(self) -> Path:
        return self.repo.repo_path / self.relative_module_path

    @property
    def relative_module_path(self) -> Path:
        return Path(self.module_id.identifier.replace(".", "/") + '' if self.is_pkg else '.py')

    @property
    def _repo_name(self) -> str:
        return self.repo.repo_name

    @property
    def repo_id(self) -> str:
        return self.repo.repo_id

    # helper functions

    def exists(self) -> bool:
        return self.local_path.exists()

    @classmethod
    def from_file_path(cls, file_path: str | Path, repo: Repo | None) -> "Module":
        if repo is None:
            repo = Repo.from_file_path(file_path)
        module_id = Identifier(
            identifier=str(Path(file_path).relative_to(repo.repo_path))
            .replace(".py", "")
            .replace("/", ".")
        )
        return cls(module_id=module_id, repo=repo)
