# django_robots_registry

A small `robots.txt` view for Django, built around independently-registered
"providers" rather than one big config block — each app that needs to
`Disallow` something owns its own rule, without needing to know about any
other app's rules or edit a shared list.

## Usage

Each app defines a `RobotSpecProvider` for whatever it needs to disallow:

```python
from django_robots_registry import RobotSpec, RobotSpecProvider

class MyAppRobots(RobotSpecProvider):
    def __call__(self) -> RobotSpec:
        return RobotSpec(user_agent="*", instruction="Disallow: /my-app")
```

Then wire the view up once, passing the providers you want included:

```python
from django_robots_registry import robots_txt_view
from myapp.robots import MyAppRobots

urlpatterns = [
    path("robots.txt", robots_txt_view(MyAppRobots())),
]
```

Instantiating a `RobotSpecProvider` also registers it into a module-level
global list — calling `robots_txt_view()` with no arguments falls back to
whatever's been instantiated globally by then, though passing providers
explicitly (as above) is less fragile with respect to import order.

`RobotSpecProvider.__call__` can return either a single `RobotSpec` or a
`Sequence[RobotSpec]` (e.g. to conditionally contribute zero, one, or more
rules based on runtime settings).

## Status

Extracted from an internal project (glotronic.net), with full commit
history preserved via `git subtree split`. Small and stable; grown
on-demand as needed.

## License

BSD-3-Clause — see [LICENSE](LICENSE).
