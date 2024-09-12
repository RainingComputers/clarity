from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime


class ParseError(Exception):
    def __init__(self) -> None:
        super().__init__(self)
        self.message = "Unable to parse lines"


@dataclass
class ParsedTimeSpan:
    start: datetime
    to: datetime
    name: str
    tags: list[str]


@dataclass
class CurrentTaskStatus:
    name: str
    remaining: int
    progress: float


def parse_timestamp(timestamp_str: str, now: datetime) -> datetime:
    hour, minute = map(int, timestamp_str.replace(".", ":").split(":"))

    return datetime(
        year=now.year, month=now.month, day=now.day, hour=hour, minute=minute
    )


def expand_tags(tags: list[str]) -> list[str]:
    expanded = deepcopy(tags)

    for tag in tags:
        if "/" in tag:
            expanded.append(tag.split("/")[0])

    return expanded


def parse_span(line: str, now: datetime) -> ParsedTimeSpan:
    tokens = line.split(" ")

    first_tag = next(
        (idx for idx, token in enumerate(tokens) if token[0] == "#"), len(tokens)
    )

    try:
        start = parse_timestamp(tokens[0], now)
        to = parse_timestamp(tokens[2], now)
        name = " ".join(tokens[3:first_tag])
        tags = tokens[first_tag:]
    except (IndexError, ValueError) as err:
        raise ParseError() from err

    tags = expand_tags(tags)

    return ParsedTimeSpan(start=start, to=to, name=name, tags=tags)


def parse_schedule(content: str, now: datetime) -> list[ParsedTimeSpan]:
    return list(
        sorted(
            map(lambda line: parse_span(line, now), content.splitlines()),
            key=lambda parsed_line: parsed_line.start,
        )
    )


def sort_dict(unsorted: dict) -> dict:
    return dict(sorted(unsorted.items()))


def construct_time_spent_map(time_spans: list[ParsedTimeSpan]) -> dict[str, int]:
    result: dict[str, int] = {}

    for span in time_spans:
        delta_seconds = span.to - span.start

        for tag in span.tags:
            try:
                result[tag] += delta_seconds.seconds
            except KeyError:
                result[tag] = delta_seconds.seconds

    return sort_dict(result)


def get_current_task_status(
    time_spans: list[ParsedTimeSpan], time: datetime
) -> CurrentTaskStatus | None:
    for span in time_spans:
        if span.start <= time < span.to:
            remaining = (span.to - time).seconds
            progress = remaining / (span.to - span.start).seconds
            return CurrentTaskStatus(
                name=span.name, remaining=remaining, progress=progress
            )

    return None
