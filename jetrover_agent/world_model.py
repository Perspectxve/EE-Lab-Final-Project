import json, math, os, re
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple
from .messages import Entity, Relation

STOP = {'the','a','an','zone','area','place','near','with','marked','by','picture','image','sign','of','to','in','on'}

def tokens(text: str):
    return set(t for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP)

def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb: return 0.0
    return len(ta & tb) / len(ta | tb)

class WorldModel:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self._next = 1

    def add_entity(self, type_: str, description: str, pose=None, attrs=None, entity_id=None) -> Entity:
        pose = pose or {'x':0.0,'y':0.0,'z':0.0,'yaw':0.0}
        attrs = attrs or {}
        entity_id = entity_id or f'{type_}_{self._next}'
        self._next += 1
        ent = Entity(entity_id, type_, description, pose, attrs)
        self.entities[ent.id] = ent
        self._infer_regions(ent)
        return ent

    def add_relation(self, subject: str, predicate: str, object_: str):
        r = Relation(subject, predicate, object_)
        if r not in self.relations:
            self.relations.append(r)

    def _infer_regions(self, ent: Entity):
        # If we detect a landmark like "bird picture", create an abstract "bird zone".
        if ent.type in ('landmark','sign','picture','image'):
            label = ent.attrs.get('label') or ent.description.replace('picture of ', '').replace('image of ', '')
            label = label.replace('picture','').replace('image','').replace('sign','').strip()
            if label:
                zone_id = f'zone_{label.lower().replace(" ", "_")}'
                if zone_id not in self.entities:
                    self.entities[zone_id] = Entity(zone_id, 'region', f'{label} zone / tabletop near {ent.description}', dict(ent.pose), {'derived_from': ent.id})
                self.add_relation(ent.id, 'marks', zone_id)

    def query(self, phrase: str, threshold=0.45) -> Optional[Entity]:
        phrase_l = phrase.lower().strip()
        # exact id first
        if phrase_l in self.entities: return self.entities[phrase_l]
        scored = []
        for ent in self.entities.values():
            aliases = [ent.id.replace('_',' '), ent.description, ent.type]
            if 'label' in ent.attrs: aliases.append(str(ent.attrs['label']))
            score = max(jaccard(phrase_l, a) for a in aliases)
            # Special case: "bird zone" should match "picture of bird" or derived region.
            for t in tokens(phrase_l):
                if t in tokens(ent.description) or t in tokens(ent.id):
                    score += 0.25
            scored.append((score, ent))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored and scored[0][0] >= threshold else None

    def to_prompt(self) -> str:
        ents = [asdict(e) for e in self.entities.values()]
        rels = [asdict(r) for r in self.relations]
        return json.dumps({'entities': ents, 'relations': rels}, indent=2)

    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'entities':[asdict(e) for e in self.entities.values()], 'relations':[asdict(r) for r in self.relations]}, f, indent=2)

    @classmethod
    def load(cls, path):
        wm = cls()
        if not os.path.exists(path): return wm
        with open(path) as f: data = json.load(f)
        for e in data.get('entities', []): wm.entities[e['id']] = Entity(**e)
        for r in data.get('relations', []): wm.relations.append(Relation(**r))
        return wm
