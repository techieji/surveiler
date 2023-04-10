# surveiler

Very simple file-watching utility.

## Installation

(coming soon) pip:
`pip install surveiler`

Or just copy the file locally (it's literally 60 lines)

## Usage

Two exported functions: `make_event_handler`, `surveil`. Signatures (not exactly):

```py
def make_event_handler(**kw: dict[str, Callable[[], None]]) -> Callable[[int], None]: ...
def surveil(directory_name: str, event_handler: Callable[[int], None]) -> Never: ...
```

Example usage:

```py
event_handler = make_event_handler(on_create=lambda: print('create'), on_modify=lambda: print('modify'))
surveil("testdirec", event_handler)
```

Check out the constants in the source file to see what event handlers you can add; any one of them can be adapted
to a keyword argument to `event_handler`. Example: `IN_MOVE` -> `on_move`.
