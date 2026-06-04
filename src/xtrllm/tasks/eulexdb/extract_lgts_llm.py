# eulex\\data_engineering\\utils\\xtrllm\\extract_litigants.py
"""
- ExtractLitigantsTask

RULES
- The "acting on behalf of" problem: strip the representative, log the principal —
  extraction must be role-aware at parse time.

- The ",by" is usually a sign of ending litigant entry even if multiple actors,
  keep as one.
  Example: Three Ireland Services (Hutchison) Limited and Three Ireland (Hutchison) Limited

OUTPUT
LitigantEntry     →  one YAML block per entry
  principal_name  →  editable field
  principal_role      →  optional, editable (applicant / defendant / intervener etc.)
  src_string      →  audit trail, never touched after extraction
  lawyers[]       →  list, each lawyer independently editable
    Lawyer.name      →  the field you correct
    Lawyer.role      →  editable
    Lawyer.src_string → audit trail
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from xtrllm.core.base import BaseTask


# ── SCHEMA ────────────────────────────────────────────────────────────────────

class Lawyer(BaseModel):
    name: str
    role: Optional[str]   # abogado, advocaat, Agent, procuradora etc. — None if not stated

class LitigantEntry(BaseModel):
    """One entry from the litigants/parties section."""
    src_string:    str            # full raw line for provenance
    principal_name: str            # actual party — strip 'acting on behalf of' constructs
    principal_role:    Optional[str] = None   # applicant / defendant / intervener etc. — None if not stated
    lawyers:       List[Lawyer] = Field(default_factory=list)  # empty if no lawyers named

class ExtractLitigantsSchema(BaseModel):
    litigants: List[LitigantEntry] = Field(..., min_length=1)


# ── TASK ──────────────────────────────────────────────────────────────────────

SYS_MSG = """
# Task
Extract litigants and their lawyers from EU court case introductions.

# Output requirement
Return only valid structured output matching the provided schema.
Do not return explanations, commentary, or markdown fences.

# Extraction target
Extract every litigant entry, its party role if stated, and its associated lawyers.

# REQUIRED JSON SCHEMA (copy exactly)
{
  "litigants": [
    {
      "src_string": "exact raw litigant text",
      "principal_name": "cleaned name", 
      "principal_role": "role or null",
      "lawyers": [
        {
          "name": "person name only",
          "role": "title or null", 
        }
      ]
    }
  ]
}

## Rules for litigants
- Extract the litigant name exactly as written in the text.
- If the text says "X acting on behalf of Y", extract Y as `principal_name`. X belongs in the representatives block, not in `principal_name`.
- Anonymous names such as XXX, Z, LG, CY are valid `principal_name` values and must be extracted as written.
- If multiple named entities appear as separate party lines before a shared representation block, extract one litigant entry per named entity.
- If multiple entities are written inside one single litigant name string joined by "and" or "et", keep that single string as one litigant entry exactly as written.
- A litigant entry ends when the representation block begins, for example at expressions such as: `by`, `represented by`, `représenté par`, `représentée par`, `représentés par`, `représentées par`, `assisté de`, `assistée de`, `assisted by`.
- Do not include representation phrases inside `principal_name`.

## Rules for party role
- If a party role is stated, extract it exactly as written into `principal_role`.
- Examples include `applicant`, `defendant`, `intervener`, `intervening party`, `partie requérante`, `partie défenderesse`, `partie intervenante`, `parties intervenantes`.
- If no role is stated for that litigant, set `principal_role` to `null`.

## Rules for lawyers / representatives
- Extract all named lawyers or representatives associated with the litigant.
- Split multiple persons correctly when separated by commas, `and`, `et`, or phrases such as `ainsi que par`.
- For each lawyer entry extract:
  - `name`: the person name only
  - `role`: the professional title or function if stated, otherwise `null`
  - `src_string`: the exact text span corresponding to that lawyer mention
- Remove honorific or group prefixes from the individual `name` field, such as `Me`, `Mes`, `M.`, `MM.`, `Mme`, `Mmes`.
- Keep the professional role if stated, such as `avocat`, `avocate`, `abogados`, `advocaat`, `agent`, `solicitor`, `barrister`, `QC`, `Rechtsanwalt`, or `en qualité d’agent`.
- If the text uses a temporal formula such as `initialement par X puis par Y` or `initially by X and subsequently by Y`, extract all unique named persons in one flat list and ignore the timing distinction.
- If no lawyers or representatives are named, return an empty list.

## Association rules
- Lawyers belong to the nearest litigant or litigant group they represent.
- If several litigants are listed together and then a shared representation block follows, attach the same lawyers to each relevant litigant entry unless the text clearly indicates otherwise.

## Provenance
- For each litigant entry, `src_string` must contain the full raw litigant entry text as found in the source.

## Output constraints
- Return only schema-valid structured output.
- Do not invent missing names or roles.
- Use `null` for missing singular values.
- names and roles using literal Unicode characters (e.g., ‘é’, ‘ê’, ‘ç’), not escaped byte sequences like \x00e9.”
"""

class ExtractLitigantsTask(BaseTask):
    name          = "extract_lgts_llm"
    version       = "v1"
    schema        = ExtractLitigantsSchema
    system_prompt = SYS_MSG

    def build_prompt(self, text: str) -> str:
        return f"""
TEXT:
{text}

Extract all litigant entries with their name, optional party role, and lawyers.
""".strip()