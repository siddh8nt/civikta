# CIVIKTA Authority Master (reference)

Delhi authority universe for the MVP (PRD §12). Slugs are the join key used by
`routing_rules.primary_authority_slug` / `secondary_authority_slug`.

## Local-body / municipal

| Slug | Authority | Scope |
|---|---|---|
| `mcd_sanitation`    | MCD - Sanitation        | MCD area garbage / sweeping / cleanup |
| `mcd_engineering`   | MCD - Engineering       | MCD local roads, drains, footpaths, lights |
| `mcd_horticulture`  | MCD - Horticulture      | MCD parks / trees |
| `mcd_public_health` | MCD - Public Health     | stray animals / carcass |
| `ndmc_sanitation`   | NDMC - Sanitation       | NDMC garbage |
| `ndmc_civil`        | NDMC - Civil            | NDMC roads / drains / lights |
| `ndmc_horticulture` | NDMC - Horticulture     | NDMC parks / trees |
| `dcb_civic`         | Delhi Cantonment Board  | DCB civic services |

## Service-specific / citywide

| Slug | Authority | Scope |
|---|---|---|
| `djb`          | Delhi Jal Board                | water supply + sewer |
| `pwd`          | Public Works Department        | major roads / flyovers / corridors |
| `ifcd`         | Irrigation & Flood Control     | major / trunk drains, nallahs |
| `dda`          | Delhi Development Authority    | DDA land + DDA parks |
| `delhi_police` | Delhi Police                   | enforcement (encroachment / obstruction) |
| `nhai`         | National Highways Authority    | NH stretches |

See `../sql/seeds/authorities.sql` for the seeded master data.
