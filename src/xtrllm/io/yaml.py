# xtrllm/io/yaml.py

"""
Persistent YAML feature store for document-level extraction outputs.

- append_to_feature_space_from_df()	
    Appends new items to existing list	"Add missing observers"

- overwrite_feature_space_from_df()	
    Replaces entire namespace list	"Correct all observers for doc X"
LOG:
 - 2026.04.06: ADDED tqmd support for load_flat_feature_space_as_df()
"""

import yaml
from collections.abc import Collection
from pydantic import BaseModel
from pathlib import Path
from typing import Any
from tqdm import tqdm
import pandas as pd

def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}  


# def _dump(doc: dict, path: Path) -> None:
#     path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False))
def _dump(doc: dict, path: Path) -> None:
    path.write_text(yaml.dump(doc,
                              allow_unicode=True,
                              sort_keys=False,
                              default_flow_style=False,
                              width=float("inf"),)
                    )



def _resolve(value: Any) -> Any:
    return value.model_dump() if isinstance(value, BaseModel) else value


# ── PROGRAMMATIC ──────────────────────────────────────────────────────────────

def write_features(results: dict[str, dict | BaseModel], features_path: Path) -> None:
    """
    Merge pipeline outputs into the feature store, keyed by doc_id.
    USE when adding or replacing entire namespaces.

    - Existing doc_id → sibling namespaces preserved, touched namespace replaced wholesale.
    - Missing doc_id  → full results tree inserted as new entry.

    Warning:
        Namespace writes are destructive — the entire previous value is lost.
        For partial enrichment use append_to_feature_space_from_df().
        For corrective overwrites use overwrite_feature_space_from_df().
    """
    existing = _load(features_path)
    for doc_id, data in results.items():
        existing.setdefault(doc_id, {}).update(_resolve(data))
    _dump(existing, features_path)


def patch_block(doc_id: str, 
                key_path: list[str | int], 
                value: Any, features_path: Path ) -> None:
    """Replace an entire sub-structure at key_path for a given doc_id.

    The primary correction tool — use when a better pipeline rewrites a
    whole block (e.g. all lawyers for one observation) corpus-wide in a loop.

    Examples:
        # Replace all lawyers for the first observation after re-extraction
        patch_block("JDG_2008_0001_CJ_00", ["observations", 0, "lawyers"], new_lawyers, features_path)

        # Overwrite entire observations block for a doc
        patch_block("JDG_2008_0001_CJ_00", ["observations"], new_observations, features_path)
    """
    doc = _load(features_path)
    node = doc[doc_id]
    for k in key_path[:-1]:
        node = node[k]
    node[key_path[-1]] = _resolve(value)
    _dump(doc, features_path)


# ── MANUAL / HOTFIX ───────────────────────────────────────────────────────────

def append_to_feature(doc_id: str, 
                            key_path: list[str | int], 
                            item: Any, 
                            features_path: Path 
                      ) -> None:
    """Append a single item to a list at key_path. Does not replace existing items.

    Use when a missed entry is spotted manually in a handful of docs.

    Examples:
        # Add a missed lawyer to an existing lawyers list
        append_to_feature(
            "JDG_2008_0001_CJ_00", ["observations", 0, "lawyers"],
            {"name": "A. Rossi", "role": "avvocato"},
            features_path
        )
    """
    doc = _load(features_path)
    node = doc[doc_id]
    for k in key_path:
        node = node[k]
    node.append(_resolve(item))
    _dump(doc, features_path)


def patch_value(doc_id: str, 
                key_path: list[str | int], 
                value: Any, 
                features_path: Path
                ) -> None:
    """Replace a single scalar value at key_path. Manual hotfix only.

    Examples:
        # Correct a wrong language code
        patch_value("JDG_2008_0001_CJ_00", ["doc_metadata", "language"], "it", features_path)

        # Fix a principal name typo
        patch_value("JDG_2008_0001_CJ_00", ["observations", 1, "principal_name"], "INPS", features_path)
    """
    patch_block(doc_id, key_path, value, features_path)

############################################################################
# NOTE MAIN Full YML LOADER & Dumper
############################################################################
def load_yaml_store(features_path: Path) -> dict:
    """Public wrapper: Load entire feature store."""
    return _load(features_path)

def dump_yaml_store(store: dict, features_path: Path) -> None:
    """Public wrapper: Dump feature store to YAML."""
    _dump(store, features_path)


############################################################################
# NOTE Key Loader for all records 
############################################################################
def load_feature_space(features_path: Path,
                       feature_space_key: str,           # e.g., "observers"
                       doc_ids: list[str] | None = None  # Optional filter
                       ) -> dict[str, list[dict]]:
    """Load {doc_id: [records]} for a feature space. Custom unpack downstream."""
    existing = _load(features_path)
    result = {
        doc_id: data[feature_space_key]
        for doc_id, data in existing.items()
        if feature_space_key in data
    }
    return {k: v for k, v in result.items() if doc_ids is None or k in doc_ids}



# ------------------------------------------------------------------------------------------------------------------------------------------------------

###########################################################
# <> DELETE ENTIRE FEATURE SPACE 
# DELETE 
###########################################################
def delete_feature_space(feature_space_key: str,
                         features_path: Path,
                         doc_ids: list[str] | None = None,
                         keep_empty_keys: bool = True 
                         ) -> None:
    
    """Delete namespace but optionally keep empty doc_id keys."""
    existing = _load(features_path)
    target_docs = set(doc_ids) if doc_ids else existing.keys()
    for doc_id in target_docs:
        if doc_id in existing and feature_space_key in existing[doc_id]:
            existing[doc_id].pop(feature_space_key)
        
        # Keep empty doc_id keys (no cleanup)
        if keep_empty_keys and not existing[doc_id]:
            pass  # Keep empty dict {}
        else:
            # Normal cleanup - remove truly empty docs
            if not existing[doc_id]:
                del existing[doc_id]
    
    _dump(existing, features_path)
    
    
###########################################################
# <> REPLACE a single namespace for doc_ids present in df.
# 
###########################################################

def overwrite_feature_space_from_df(
    df: pd.DataFrame,
    doc_id_col: str,
    feature_space_key: str,
    item_cols: list[str],
    features_path: Path,
    *,
    expected_ids: Collection[str] | None = None,
) -> None:
    """
    Surgically overwrite a single namespace for doc_ids present in df.

    Unlike dump_flat_feature_space_from_df, this preserves ALL other
    doc_ids and ALL other namespaces. Only `feature_space_key` entries
    for doc_ids found in df are fully replaced (not merged/appended).

    Args:
        df:                Source DataFrame with corrected records.
        doc_id_col:        Column identifying the document.
        feature_space_key: The namespace to overwrite wholesale.
        item_cols:         Payload columns to persist.
        features_path:     Target YAML path.
        expected_ids:      Optional safety gate — raises ValueError
                           if any declared id is absent from df.
                           Useful when you know exactly which ids
                           were corrected and want to enforce it.
    """
    if expected_ids is not None:
        missing = set(expected_ids) - set(df[doc_id_col].unique())
        if missing:
            raise ValueError(
                f"Declared expected_ids not found in df: {missing}"
            )

    existing = _load(features_path)

    for doc_id, group in df.groupby(doc_id_col):
        if doc_id not in existing:
            existing[doc_id] = {}
        # Full namespace replacement — intentionally no merge
        existing[doc_id][feature_space_key] = (
            group[item_cols].to_dict(orient="records")
        )

    _dump(existing, features_path)

###########################################################
# <> dump_flat_feature_space_from_df 
# DUMP docid + namespace_key + List[col_name: [str|int]]
###########################################################
def dump_flat_feature_space_from_df(df: pd.DataFrame,
                                    doc_id_col: str,          # 1st: the pivot
                                    feature_space_key: str,   # 2nd: the feature Namespace
                                    item_cols: list[str],     # 3rd: the payload columns
                                    features_path: Path,      # 4th: the target YAML
                                    ) -> None:
    """
    **Overwrites Docs & Entire Namespace**
    Dump a flat DataFrame as a feature list under doc_id.
    All features go through this one gate.
    """
    
    results = {
        doc_id: {feature_space_key: group[item_cols].to_dict(orient="records")}
        for doc_id, group in df.groupby(doc_id_col)}
    
    write_features(results, features_path) # type: ignore

###########################################################
# <> load_flat_feature_space_as_df 
# LOAD docid + namespace_key + List[col_name: [str|int]]
###########################################################

def load_flat_feature_space_as_df(features_path: Path, 
                                  feature_space_key: str, 
                                  doc_ids: list[str] | None = None 
                                  ) -> pd.DataFrame:
    """Load feature space directly to flat DF with doc_id column."""
    existing = _load(features_path)
    rows = []
    target_docs = set(doc_ids) if doc_ids else None
    
    # Wrap the items with tqdm for progress bar
    for doc_id, data in tqdm(existing.items(), 
                             desc=f"Loading '{feature_space_key}' YML"):
        if target_docs and doc_id not in target_docs:
            continue
        if feature_space_key in data:
            for rec in data[feature_space_key]:
                rows.append({"doc_id": doc_id, **rec})
    
    return pd.DataFrame(rows)


###########################################################
# < > append_to_feature_space
# 
###########################################################

def append_to_feature_space_from_df(df: pd.DataFrame,
                                    doc_id_col: str,
                                    feature_space_key: str,
                                    item_cols: list[str],
                                    features_path: Path,
                                    ) -> None:
    """
    Append df rows as new items under doc_id → feature_space_key.

    Args:
        df:                Source DataFrame, one row per item.
        doc_id_col:        Column used as the top-level YAML key.
        feature_space_key: List key nested under each doc_id.
        item_cols:         Columns to write into each list item.
        features_path:     Path to the target YAML file.
    """
    existing = _load(features_path)

    for doc_id, group in df.groupby(doc_id_col):
        if doc_id not in existing:
            existing[doc_id] = {}
        if feature_space_key not in existing[doc_id]:
            existing[doc_id][feature_space_key] = []

        for _, row in group[item_cols].iterrows():
            existing[doc_id][feature_space_key].append(row.to_dict())

    _dump(existing, features_path)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

#########################################################
# <> dump_tabular_space
# DUMP docid + namespace_key + cols[List|dict|str|int]
#########################################################
def dump_tabular_space(df: pd.DataFrame,
                       doc_id_col: str,
                       feature_space_key: str,
                       features_path: Path
                       ) -> None:

    """Dump DataFrame rows as tabular list under doc_id/namespace.
    Perfect roundtrip with load_tabular_space. Serializes contained dicts/lists as-is.
    
    Pre-select columns if subset needed: df_subset = df[cols].
    """
    results = { 
               doc_id: group.to_dict(orient="records")
               for doc_id, group in df.groupby(doc_id_col)
               }
    
    write_features({doc_id: {feature_space_key: records} 
                    for doc_id, records in results.items()},  # type: ignore
                   features_path)


def load_tabular_space(features_path: Path,
                       feature_space_key: str,
                       doc_ids: list[str] | None = None
                       ) -> pd.DataFrame:
    """Load namespace back to exact original DataFrame shape.
    
    Recovers ALL dumped columns. Preserves contained dicts/lists.
    Filters by doc_ids if provided (empty DF if none found).
    """
    
    existing = _load(features_path)
    rows = []
    target_docs = set(doc_ids) if doc_ids else None
    
    for doc_id, data in existing.items():
        if target_docs and doc_id not in target_docs:
            continue
        if feature_space_key in data:
            rows.extend(data[feature_space_key])
    
    return pd.DataFrame(rows)




    
#################################################
# PROVISIONAL END   -----------------------------
#################################################


# NOTE 
# - WRITE Features works at the doc level always. 

EXAMPLE001 =""" 
data_view = []
for docid, metafeats in doc_meatadata.items():
    if not metafeats[0]['procedure_name']:
        
        entry = {'docid':docid, 
                 'procedure_name':''}
        data_view.append(entry)

pd.DataFrame(data_view)
"""



EXAMPLE4 = """ 
# Equivalent normal code:
new_dict = {}
for docid, namespaces in feats_space.items():
    new_dict[docid] = {k: v for k in namespaces if k != 'pito'}
feats_space = new_dict

# One-liner version
feats_space = {
    docid: {k: v for k in namespaces if k != 'pito'}
    for docid, namespaces in feats_space.items()
}
"""


EXAMPLE3 = """
# 1. Generic load (works for ANY structure)
space = load_feature_space(path, "lawyers_llm")

# 2. Custom unpack: pivot on (doc_id, principal_name)
def unpack_lawyers_principal(space: dict[str, list[dict]]) -> pd.DataFrame:
    rows = []
    for doc_id, observations in space.items():
        for obs in observations:
            principal = obs["principal_name"]
            for lawyer in obs.get("lawyers", []):
                rows.append({
                    "doc_id": doc_id,
                    "principal_name": principal,
                    "lawyer_name": lawyer["name"],
                    "lawyer_role": lawyer["role"]
                })
    return pd.DataFrame(rows)

df_analysis = unpack_lawyers_principal(space)
# doc_id | principal_name | lawyer_name | lawyer_role ✓
"""

EXAMPLE2 = r""" 
Tabular Feature Store API (doc_id → namespace → records)

Three canonical loading paths from single YAML:

- `load_feature_space` → {doc_id: [records]}     Base unit, max flexibility
- `load_feature_space_flat` → DF(doc_id + cols)  Analysis tables  
- `load_tabular_space` → DF(exact shape)         Pipeline roundtrip

All mirror matching dumpers. doc_id is the key.
"""

EXAMPLE1 = """ 

# Example instance
lawyers_result = ExtractLawyersSchema.parse_obj({
    "actors": [
        {
            "name": "Mrs. Smith",
            "lawyers": [
                {"name": "A. Rossi", "src_string": "A. Rossi avvocato"},
                {"name": "B. Bianchi", "src_string": "B. Bianchi, lawyer"}
            ]
        },
        {
            "name": "Mr. Jones",
            "lawyers": [
                {"name": "C. Verdi", "src_string": "C. Verdi, legal counsel"}
            ]
        }
    ]
})

write_features(
    {
        "JDG_2008_0001_CJ_00": {
            "lawyers_llm": lawyers_result.model_dump()
            }
    },
    features_path = FEATURES_YML 
    )

# For your observers list:
append_to_feature(doc_id, ["observers"], new_obs, FEATURES_YML)

append_to_feature(
    "JDG_2008_0001_CV_00",
    ["observers"],  # path to the list
    {"actor_id": "ACT_NEW_001", "actor_name_db": "New Party", "actor_class": "ACT_TYPE_EU_INST"},
    FEATURES_YML
)

# First item cols is the key 
dump_feature_flat(
    df            = doc_jdgs_obs_df,
    doc_id_col    = "doc_id",
    feature_key   = "llm_observers",
    item_cols     = ["actor_id", "actor_name_db", "actor_class", "lawyer_name", "lawyer_src_string"],
    features_path = FEATURES_YML,

"""