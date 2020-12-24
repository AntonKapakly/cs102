import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        # PUT YOUR CODE HERE
        values = self[:-1] + (self[-1].encode(),)
        len_name = len(self.name.encode())
        t = 8 - (6 + len(self.name)) % 8
        packed = struct.pack(f">10I20sh{len_name}s{t}x", *values)
        return packed

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        # PUT YOUR CODE HERE
        form = ">10I20sh"
        len_name = data.find(b"\x00", struct.calcsize(form)) - struct.calcsize(form)
        form += f"{len_name}s{8 - (6 + len_name) % 8}x"
        res = struct.unpack_from(form, data)
        return GitIndexEntry(
            res[0],
            res[1],
            res[2],
            res[3],
            res[4],
            res[5] & 0xFFFFFFFF,
            res[6],
            res[7],
            res[8],
            res[9],
            res[10],
            res[11],
            res[12].decode(),
        )


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    # PUT YOUR CODE HERE
    entries = []
    path = gitdir / "index"
    if path.exists():
        with path.open("rb") as file:
            content = file.read()
        title = struct.unpack_from("!4sLL", content)
        j = struct.calcsize("!4sLL")
        for i in range(title[2]):
            entry = GitIndexEntry.unpack(content[j:])
            entry_len = struct.calcsize(
                f">10I20sh{len(entry.name)}s{8 - (6 + len(entry.name)) % 8}x"
            )
            j += entry_len
            entries.append(entry)
        sha = content[j:].hex()
        return sorted(entries, key=lambda x: x.name)
    return entries


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    # PUT YOUR CODE HERE
    content = struct.pack("!4sLL", "DIRC".encode(), 2, len(entries))
    for e in entries:
        content += e.pack()
    content += hashlib.sha1(content).digest()
    with open(gitdir / "index", "wb") as file:
        file.write(content)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    # PUT YOUR CODE HERE
    index = read_index(gitdir)
    if details:
        for i in index:
            print(oct(i.mode)[2:], i.sha1.hex(), 0, end="\t")
            print(i.name)
    else:
        print("\n".join([i.name for i in index]))


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    # PUT YOUR CODE HERE
    entries = read_index(gitdir)
    for p in paths:
        stat = os.stat(p)
        with p.open("r") as file:
            content = file.read().encode()
        sha1 = hash_object(content, fmt="blob", write=write, hex=False)
        if isinstance(sha1, str):
            sha1 = sha1.encode()
        entries.append(
            GitIndexEntry(
                int(stat.st_ctime),
                0,
                int(stat.st_mtime),
                0,
                stat.st_dev,
                stat.st_ino & 0xFFFFFFFF,
                stat.st_mode,
                stat.st_uid,
                stat.st_gid,
                stat.st_size,
                sha1,
                7,
                "/".join(p.parts),
            )
        )
    write_index(gitdir, entries)
