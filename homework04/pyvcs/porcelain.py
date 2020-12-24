import os
import pathlib
import typing as tp

from pyvcs.index import ls_files, read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    update_index(gitdir, paths)


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    entries = read_index(gitdir)
    return commit_tree(gitdir, write_tree(gitdir, entries), message, author=author)


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    for i in read_index(gitdir):
        if i != gitdir:
            path = pathlib.Path(i.name)
            try:
                os.remove(path)
                for p in path.parents:
                    p.rmdir()
            except OSError:
                pass
    form, content = read_object(obj_name, gitdir)
    sha = commit_parse(content)
    for paths, content in find_tree_files(sha, gitdir):  # type:ignore
        if not paths.parent.exists():
            paths.parent.mkdir(parents=True)
        with paths.open("w") as file:
            file.write(content)  # type:ignore
