import typing as tp
from collections import defaultdict
from time import strptime


def parse(file: str) -> tp.DefaultDict[str, tp.DefaultDict[str, tp.List[str]]]:
    data: tp.DefaultDict[str, tp.DefaultDict[str, tp.List[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    with open(file, "r") as raw_file:
        for line in raw_file.readlines():
            process_line(data, line)
            if params["END"]:
                break
    return data


def process_line(data: tp.DefaultDict[str, tp.DefaultDict[str, tp.List[str]]], line: str) -> None:
    comment_idx = line.find("--")
    elements = line[:comment_idx].split()
    if len(elements) == 1:
        (keyword,) = elements
        if keyword == "/":
            for keys in params:
                params[keys] = False
        if keyword in params.keys():
            params[keyword] = True
        return
    if params["DATES"]:
        params["DATES"] = False
        parse_date(elements)
        return
    if params["KEYWORD"]:
        if len(elements) == 1 and elements[0] == "/":
            params["KEYWORD"] = False
        elif elements:
            parse_events(data, elements)
        return
    if params["END"]:
        return


def parse_events(
    data: tp.DefaultDict[str, tp.DefaultDict[str, tp.List[str]]], elements: tp.List[str]
) -> None:
    key_id, *events = elements
    values: tp.List[str] = []
    for event in events:
        if event == "/":
            break
        if "*" in event:
            for t in range(int(event[:-1])):
                values.append(default_value(len(values)))
        else:
            values.append(event)

    data[current_date][key_id].extend(values)


def default_value(num: int) -> str:
    return f"D{num + 1}"


def parse_date(elems: tp.List[str]) -> None:
    day, month, year, _ = elems
    global current_date
    current_date = f"{day}.{strptime(month, '%b').tm_mon:02}.{year}"


def prettify(data: tp.DefaultDict[str, tp.DefaultDict[str, tp.List[str]]]) -> str:
    pretty = ""
    for date in data:
        pretty += f"{date}:\n"
        for key in data[date]:
            events = " ".join(data[date][key])
            pretty += f"\t {key} - [{events}]\n"
    return pretty


params = {"DATES": False, "KEYWORD": False, "END": False}
current_date = ""

file = "file.txt"
parsed = parse(file)
print(parsed)
print(prettify(parsed))
