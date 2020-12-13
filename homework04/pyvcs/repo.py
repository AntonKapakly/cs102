import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    # PUT YOUR CODE HERE
    if isinstance(workdir, str):
        workdir = pathlib.Path(workdir)
    a = [workdir]
    while a:
        current = a.pop()
        for path in current.iterdir():
            if path.is_dir():
                if path.name == ".git":
                    return path
                a.append(path)
    for path in workdir.parents:
        if path.name == ".git":
            return path

    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    # PUT YOUR CODE HERE
    if isinstance(workdir, str):
        workdir = pathlib.Path(workdir)
    if workdir.exists() and workdir.is_file():
        raise Exception(f"{workdir} is not a directory")
    name = os.getenv("GIT_DIR", default=".git")

    (workdir / name).mkdir()
    (workdir / name / "refs" / "heads").mkdir(parents=True)
    (workdir / name / "refs" / "tags").mkdir(parents=True)
    (workdir / name / "objects").mkdir()
    with (workdir / name / "HEAD").open("w") as file:
        file.write("ref: refs/heads/master\n")
    with (workdir / name / "config").open("w") as file:
        file.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
        )
    with (workdir / name / "description").open("w") as file:
        file.write("Unnamed pyvcs repository.\n")
    return workdir / name
