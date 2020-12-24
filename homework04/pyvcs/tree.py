import os
import pathlib
import stat
import time
import typing as tp
from collections import defaultdict

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


class TreeObject(tp.NamedTuple):
    mode: int
    name: str
    sha1: bytes


directory_mode = 16384


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:

    path_to_object: tp.Dict[str, tp.Union[GitIndexEntry, TreeObject]] = {}
    childs: tp.DefaultDict[str, tp.List[str]] = defaultdict(list)
    for entry in index:
        path_to_object["./" + entry.name] = entry
    for i in index:
        parts = ["."] + list(pathlib.Path(i.name).parts)
        for j, part in enumerate(parts):
            parent = "/".join(parts[:j])
            child = "/".join(parts[: j + 1])
            if child not in path_to_object:
                path_to_object[child] = TreeObject(directory_mode, part, b"")
            childs[parent].append(child)

    Q: tp.List[str] = ["."]
    while Q:
        path = Q.pop()
        if path in childs:
            if not any([i in childs for i in childs[path]]):
                data = b""
                for object_path in childs[path]:
                    object = path_to_object[object_path]
                    data += str(oct(object.mode)[2:]).encode()
                    data += b" "
                    data += pathlib.Path(object.name).parts[-1].encode()
                    data += b"\x00"
                    data += object.sha1
                    sha = hash_object(data, "tree", True, False)
                    prev_object = path_to_object[path]
                    if isinstance(sha, str):
                        sha = sha.encode()
                    path_to_object[path] = TreeObject(prev_object.mode, prev_object.name, sha)
                    if path in childs:
                        childs.pop(path)
            else:
                Q.append(path)
                for entry_path in childs[path]:
                    Q.append(entry_path)

    return path_to_object[childs[""][0]].sha1.hex()


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    if not author:
        author = (
            os.getenv("GIT_AUTHOR_NAME", default="Anton")
            + " <"
            + os.getenv("GIT_AUTHOR_EMAIL", default="kapakly0@gmail.com")
            + ">"
        )
    data = ""
    data += f"tree {tree}\n"
    if parent:
        data += f"parent {parent}\n"
    if author:
        j = time.timezone
        j = j // 60
        sign = "+" if j < 0 else "-"
        hhmm = "%02d%02d" % divmod(abs(j), 60)
        name = sign + hhmm
        timestamp = f"{int(time.mktime(time.localtime()))} {name}"
        data += f"author {author} {timestamp}\n"
        data += f"committer {author} {timestamp}\n"
    data += f"\n{message}\n"
    sha = hash_object(data.encode(), "commit", True)
    if isinstance(sha, bytes):
        sha = sha.decode()
    return sha
