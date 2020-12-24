import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(
    data: bytes, fmt: str, write: bool = False, hex: bool = True
) -> tp.Union[str, bytes]:
    title = f"{fmt} {len(data)}\x00"
    content = title.encode() + data
    hashs = hashlib.sha1(content).hexdigest()
    if write:
        compress = zlib.compress(content)
        gitdir = repo_find(".")
        compress = zlib.compress(content)
        dirs = gitdir / "objects" / hashs[:2]
        if not dirs.exists() and not dirs.is_dir():
            dirs.mkdir(parents=True)
        filepath = dirs / hashs[2:]
        if not filepath.exists():
            with filepath.open("wb") as compressed_file:
                compressed_file.write(compress)
    if hex:
        return hashs
    return hashlib.sha1(content).digest()


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    # PUT YOUR CODE HERE
    if len(obj_name) < 4:
        raise Exception(f"Not a valid object name {obj_name}")
    path = gitdir / "objects" / obj_name[:2]
    if not path.exists():
        raise Exception(f"No such directory {path}")
    objects = []
    for p in path.iterdir():
        if p.name.startswith(obj_name[2:]):
            objects.append(p.parents[0].name + p.name)
    if not objects:
        raise Exception(f"Not a valid object name {obj_name}")
    return objects


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    path = gitdir / "objects" / obj_name[:2]
    for i in path.iterdir():
        if i.name.startswith(obj_name[2:]):
            return obj_name[:2] + "/" + i.name
    raise Exception("File not found")


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    # PUT YOUR CODE HERE
    path = gitdir / "objects" / find_object(sha, gitdir)
    with path.open("rb") as file:
        data = zlib.decompress(file.read())
    start = data.find(b" ")
    end = data.find(b"\x00")
    form = data[:start].decode()
    content = data[end + 1 :]
    return form, content


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    # PUT YOUR CODE HERE
    result = []
    rights = 0
    s = data.split(b" ")
    for i, item in enumerate(s):
        if i == 0:
            rights = int(item.decode())
        else:
            pos = item.find(b"\x00")
            name = item[:pos].decode()
            item = item[pos + 1 :]
            sha = item[:20].hex()
            item = item[20:]
            result.append((rights, sha, name))
            if i < len(s) - 1:
                rights = int(item.decode())
    return result


def cat_file(obj_name: str, pretty: bool = True) -> None:
    # PUT YOUR CODE HERE
    gitdir = repo_find(".")
    form, content = read_object(obj_name, gitdir)
    if pretty:
        if form == "commit":
            print(content.decode())
        elif form == "tree":
            for part in read_tree(content):
                form, _ = read_object(part[1], gitdir)
                print(f'{"0" * (6 - len(str(part[0]))) + str(part[0])} {form} {part[1]}\t{part[2]}')
        else:
            print(content.decode())
    else:
        print(content)


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[pathlib.Path, str]]:
    # PUT YOUR CODE HERE
    result = []
    a = [(tree_sha, pathlib.Path("."))]
    while a:
        v, path = a.pop()
        form, data = read_object(v, gitdir)

        if form == "tree":
            items = read_tree(data)
            for item in items:
                a.append((item[1], path / item[2]))
        else:
            form, data = read_object(v, gitdir)
            result.append((path, data.decode()))
    return result


def commit_parse(data: bytes, start: int = 0, dct=None) -> str:
    tree_sha = data[5:45].decode()
    return tree_sha
