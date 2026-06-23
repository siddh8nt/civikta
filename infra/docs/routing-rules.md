# CIVIKTA Routing Rules (reference)

Routing is **deterministic** (PRD §22). The LLM/agent classifies the issue and
infers hints; the routing engine then maps `(local_body_type, issue_type,
asset_type, road_class, drain_type, land_owner_hint)` to an authority via the
`routing_rules` table.

## Evaluation order

Rules are evaluated by `rule_priority` ascending — **lower number wins first**.
A rule matches when every non-null column on the rule equals the input (null on
the rule = wildcard). The first matching rule (lowest priority number) is used.

```
10  -> service-specific overrides (DJB water/sewer, etc.)
20  -> corridor / trunk overrides (PWD arterial, IFCD trunk drain)
40  -> ownership overrides (DDA parks)
50  -> local body defaults by issue type
60  -> encroachment / obstruction (owner + police)
200 -> per-local-body catch-all fallback
```

## Core heuristics (PRD §13)

| Issue | Route to |
|---|---|
| Garbage / sweeping | MCD / NDMC / DCB by local body |
| No water / dirty water | DJB |
| Sewer overflow | DJB (+ local sanitation cleanup) |
| Pothole on local lane | local body engineering |
| Pothole on arterial / flyover | PWD |
| Clogged local drain | local body engineering |
| Trunk drain / nallah | IFCD |
| Corridor waterlogging | PWD (escalate IFCD) |
| Park issue | by park owner (MCD / NDMC / DDA) |
| Encroachment | asset owner; co-tag Delhi Police if obstruction |
| Stray dog / carcass | local body public health |

## Co-routing
Secondary authority is set when a fix needs two bodies (e.g. sewer overflow →
DJB primary + MCD sanitation secondary).

See `../sql/seeds/routing_rules.sql` for the seeded rule set.
