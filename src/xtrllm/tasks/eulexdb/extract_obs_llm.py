# eulex\data_engineering\utils\xtrllm\extract_observers.py
"""
- ExtractObservationsTask

RULES
- The "acting on behalf of" problem you just identified is actually a signal 
that the observers section mixes principals and representatives in the raw text, which means your extraction needs to be role-aware at parse time — strip the representative, log the principal — rather than just taking the first named entity.

- The ",by" is usually a sign of ending observer even if multiple actors keep as one. 
Three Ireland Services (Hutchison) Limited and Three Ireland (Hutchison) Limited

OUTPUT
ObservationEntry  →  one YAML block per entry
  principal_name  →  editable field
  src_string      →  audit trail, never touched after extraction
  lawyers[]       →  list, each lawyer independently editable
    Lawyer.name   →  the field you correct (Pieter fix)
    Lawyer.role   →  editable
    Lawyer.src_string → audit trail


"""

from pydantic import BaseModel, Field
from typing import List, Optional
from xtrllm.core.base import BaseTask


# ── SCHEMA ────────────────────────────────────────────────────────────────────

class Lawyer(BaseModel):
    name: str
    role: Optional[str]   # abogado, advocaat, Agent, procuradora etc. — None if not stated

class ObservationEntry(BaseModel):
    """One entry from the written observations section."""
    src_string:     str            # full raw line for provenance
    principal_name: str            # actual observer/author — strip 'acting on behalf of' constructs
    lawyers:        List[Lawyer] = Field(default_factory=list)  # empty if no lawyers named

class ExtractObservationsSchema(BaseModel):
    observations: List[ObservationEntry] = Field(..., min_length=1)


# ── TASK ──────────────────────────────────────────────────────────────────────

SYS_MSG = """You are an expert in extracting structured data from EU Court of Justice observation sections.

# Task
Extract all written observation entries and their associated lawyers.

# Rules

## Principal (actor)
- Extract the name EXACTLY as written in the text
- If the entry reads "X acting on behalf of Y", extract Y as principal_name — X is their representative
- Do NOT include "acting on behalf of" in principal_name
- Anonymous persons (XXX, Z, LG, CY etc.) are valid principal names — extract as-is
- If two entities are joined by "and" in the same observation line, 
  keep them as a single principal_name — do NOT split into separate entries
- A line ending with ",by" signals the end of the principal entry — 
  everything after "by" belongs to the lawyers block


## Lawyers
- Split multiple lawyers correctly: they are separated by commas and/or "and"
- Each lawyer entry must have:
  - name: cleaned lawyer name only (no role suffix)
  - role: their title if stated (abogado, advocaat, Agent, procuradora etc.), else null
  - src_string: exact string as found in text
- If lawyers appear in "initially by X and subsequently by Y" constructs,
  extract ALL unique names in a flat list — ignore the temporal distinction
- If no lawyers are named, return an empty list

## Provenance
- src_string at entry level: full raw observation line as found in text

# Output
Return only valid structured output. No explanations, no extra text.
- names and roles using literal Unicode characters (e.g., ‘é’, ‘ê’, ‘ç’), not escaped byte sequences like \x00e9.”
"""

class ExtractObservationsTask(BaseTask):
    name          = "extract_obs_llm"
    version       = "v1"
    schema        = ExtractObservationsSchema
    system_prompt = SYS_MSG
    
    def build_prompt(self, text: str) -> str:
        return f"""
TEXT:
{text}

Extract all observation entries with their principal and lawyers.
""".strip()


# ── RETRIEVAL  ──────────────────────────────────────────────────────────────────────

# import yaml
# result = ExtractObservationsTask().run(text)
# # Assumes yaml_data exists 
# yaml_data[doc_id] = [entry.model_dump() for entry in result.observations]

# with open("feature.yaml", "w") as f:
#     yaml.dump(yaml_data, f, allow_unicode=True)
