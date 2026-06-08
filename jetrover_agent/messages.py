import json
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

@dataclass
class Entity:
    id: str
    type: str
    description: str
    pose: Dict[str, float]
    attrs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Relation:
    subject: str
    predicate: str
    object: str

@dataclass
class Action:
    action: str
    target: Optional[str] = None
    object: Optional[str] = None
    destination: Optional[str] = None
    notes: str = ''


def dumps(obj: Any) -> str:
    if hasattr(obj, '__dataclass_fields__'):
        return json.dumps(asdict(obj))
    return json.dumps(obj)


def loads(s: str, default=None):
    try:
        return json.loads(s)
    except Exception:
        return default
