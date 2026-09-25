from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse


@dataclass(frozen=True)
class RobotSpec:
    user_agent: str
    instruction: str


class _RobotSpecProviderBase(ABC):
    def __init__(self) -> None:
        self._collect(self)
        _robots.append(self)

    @abstractmethod
    def __call__(self) -> Sequence[RobotSpec] | RobotSpec: ...

    @abstractmethod
    def _collect(self) -> None: ...


_robots: list[RobotSpecProviderBase] = []


class RobotSpecProvider(_RobotSpecProviderBase):
    def _collect(self) -> None:
        _robots.append(self)


def robots_txt_view(*robots: RobotSpecProvider) -> Callable[[HttpRequest], HttpResponse]:
    specs_providers = list(robots) if len(robots) else _robots

    def view(request: HttpRequest) -> HttpResponse:
        return robots_txt(specs_providers)

    return view


def robots_txt(providers: Sequence[RobotSpecProvider]) -> HttpResponse:
    specs: list[RobotSpec] = []
    for p in providers:
        mixed = p()
        if isinstance(mixed, RobotSpec):
            specs.append(mixed)
        else:
            specs.extend(mixed)

    instructions_by_ua: dict[str, list[str]] = {}
    for spec in specs:
        instructions = instructions_by_ua.get(spec.user_agent, [])
        instructions.append(spec.instruction)
        instructions_by_ua[spec.user_agent] = instructions

    body = ""
    for ua, instructions in instructions_by_ua.items():
        body = body + f"\n{ua}\n{'\n'.join(instructions)}"

    return HttpResponse(body, content_type="text/plain")
