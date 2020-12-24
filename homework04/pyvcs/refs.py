import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    # PUT YOUR CODE HERE
    if isinstance(ref, str):
        ref = pathlib.Path(ref)
    dirs = gitdir / ref
    dirs.touch()
    dirs.write_text(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    # PUT YOUR CODE HERE
    ...


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    # PUT YOUR CODE HERE
    if refname == "HEAD":
        return str(resolve_head(gitdir))
    path = gitdir / refname
    if not path.exists():
        raise Exception(f"No such ref {refname}")
    with path.open("r") as f:
        result = f.read()
    return result


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    # PUT YOUR CODE HERE
    if (gitdir / get_ref(gitdir)).exists():
        return ref_resolve(gitdir, get_ref(gitdir))
    else:
        return None


def is_detached(gitdir: pathlib.Path) -> bool:
    # PUT YOUR CODE HERE
    return get_ref(gitdir) != "refs/heads/master"


def get_ref(gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    with (gitdir / "HEAD").open("r") as f:
        content = f.readline()
        if content.startswith("ref:"):
            ref = content[5:-1]
        else:
            ref = content
    return ref
