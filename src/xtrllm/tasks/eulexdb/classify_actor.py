""" 
Classify Actors for EulexDB Schema

"""
from pydantic import BaseModel
from xtrllm.core.base import BaseTask
from enum import Enum

class ActorType(str, Enum):
    ACT_TYPE_EU_INST = "ACT_TYPE_EU_INST"
    ACT_TYPE_EU_MS = "ACT_TYPE_EU_MS"
    ACT_TYPE_NAT_COURT = "ACT_TYPE_NAT_COURT"
    ACT_TYPE_FIRM = "ACT_TYPE_FIRM"
    ACT_TYPE_PERSON = "ACT_TYPE_PERSON"
    ACT_TYPE_EFTA_MS = "ACT_TYPE_EFTA_MS"
    ACT_TYPE_ORG_SPORT = "ACT_TYPE_ORG_SPORT"
    ACT_TYPE_ORG_LAB = "ACT_TYPE_ORG_LAB"
    ACT_TYPE_GOV_OFFIC_REG = "ACT_TYPE_GOV_OFFIC_REG"
    ACT_TYPE_GOV_INST_NAT = "ACT_TYPE_GOV_INST_NAT"
    ACT_TYPE_GOV_CIT = "ACT_TYPE_GOV_CIT"
    ACT_TYPE_GOV_INST_CIT = "ACT_TYPE_GOV_INST_CIT"
    ACT_TYPE_ORG_INDUST = "ACT_TYPE_ORG_INDUST"
    ACT_TYPE_THIRD_STATE = "ACT_TYPE_THIRD_STATE"
    ACT_TYPE_GOV_DIST = "ACT_TYPE_GOV_DIST"
    ACT_TYPE_GOV_INST_NAT_CIT = "ACT_TYPE_GOV_INST_NAT_CIT"
    ACT_TYPE_ORG_EDUC = "ACT_TYPE_ORG_EDUC"
    ACT_TYPE_ORG_NON_PROF = "ACT_TYPE_ORG_NON_PROF"
    ACT_TYPE_ORG_PROF = "ACT_TYPE_ORG_PROF"
    ACT_TYPE_GOV_INST_DIST = "ACT_TYPE_GOV_INST_DIST"
    ACT_TYPE_ORG_CONS = "ACT_TYPE_ORG_CONS"
    ACT_TYPE_GOV_INST_REG = "ACT_TYPE_GOV_INST_REG"
    ACT_TYPE_GOV_REG = "ACT_TYPE_GOV_REG"
    ACT_TYPE_GOV_OFFIC_NAT = "ACT_TYPE_GOV_OFFIC_NAT"
    ACT_TYPE_ORG_REL = "ACT_TYPE_ORG_REL"
    ACT_TYPE_GOV_INST_NAT_REG = "ACT_TYPE_GOV_INST_NAT_REG"
    ACT_TYPE_EU_DA = "ACT_TYPE_EU_DA"
    ACT_TYPE_EFTA_INST = "ACT_TYPE_EFTA_INST"
    ACT_TYPE_ORG_IO = "ACT_TYPE_ORG_IO"
    ACT_TYPE_GOV_OFFIC_CIT = "ACT_TYPE_GOV_OFFIC_CIT"
    ACT_TYPE_GOV_OFFIC_UNSPEC = "ACT_TYPE_GOV_OFFIC_UNSPEC"
    ACT_TYPE_GOV_OFFIC_DIST = "ACT_TYPE_GOV_OFFIC_DIST"
    ACT_TYPE_ORG_POL = "ACT_TYPE_ORG_POL"
    ACT_TYPE_GOV_INST_UNSPEC = "ACT_TYPE_GOV_INST_UNSPEC"
    ACT_TYPE_UNSPEC = "ACT_TYPE_UNSPEC"
    ACT_TYPE_GOV_INST_REG_CIT = "ACT_TYPE_GOV_INST_REG_CIT"
    ACT_TYPE_EU_BODY = "ACT_TYPE_EU_BODY"
    ACT_TYPE_EU_CB = "ACT_TYPE_EU_CB"
    ACT_TYPE_EU_MISC = "ACT_TYPE_EU_MISC"


class EulexDBActorSchema(BaseModel):
    actor_type: ActorType
    
SYS_MSG = """You are an expert in classifying actors into predefined institutional categories.

# Task
Classify the given actor into EXACTLY ONE of the predefined actor types.

# Rules
- Choose the SINGLE best matching category.
- Prefer the most specific category available.
- If uncertain, choose ACT_TYPE_UNSPEC.
- Do NOT interpret short two‑letter codes (e.g., CZ, BY, NZ, CE, CB, EC, ET, EU) as countries or institutions unless the full explicit name is present (e.g., 'European Commission', 'Court of Justice of the European Union', 'Czech Republic').
- Treat short letter pairs like CE, CB, EC, ET, EU, CZ, BY, NZ, GB, UK, etc. as ACT_TYPE_PERSON if they appear in the context of anonymized initials; otherwise default to ACT_TYPE_UNSPEC if role is unclear.

NOT a court:
- "Procura della Repubblica presso il Tribunale di Cagliari" → ACT_TYPE_GOV_INST_NAT
- "Parchetul de pe lângă Înalta Curte..." → ACT_TYPE_GOV_INST_NAT
- "Maria Maddalena Acernese et 656 autres juges de paix" → ACT_TYPE_PERSON
- "Präsidentin des Landesgerichts Feldkirch" → ACT_TYPE_GOV_OFFIC_NAT
-Komornik Sądowy przy Sądzie Rejonowym w Szczecinku → ACT_TYPE_GOV_OFFIC_CIT 

IS a court:
- "Tribunale di Milano" → ACT_TYPE_NAT_COURT
- "Sąd Okręgowy w Koszalinie" → ACT_TYPE_NAT_COURT
# Actor Types

ACT_TYPE_EU_INST = Core EU institutions (e.g., European Commission, European Parliament, Court of Justice)
ACT_TYPE_EU_MS = EU member states (countries)
ACT_TYPE_NAT_COURT = National courts within EU member states
ACT_TYPE_FIRM = Private companies or commercial firms
ACT_TYPE_PERSON = Individual human beings (usually initials for anonymity reasons like GB, UK or TN, ZZ)
ACT_TYPE_EFTA_MS = EFTA member states (e.g., Norway, Iceland)
ACT_TYPE_ORG_SPORT = Sports organizations
ACT_TYPE_ORG_LAB = Labor unions or worker organizations
ACT_TYPE_GOV_OFFIC_REG = Regional-level government officials
ACT_TYPE_GOV_INST_NAT = National-level government institutions (ministries, agencies)
ACT_TYPE_GOV_CIT = Cities or municipalities
ACT_TYPE_GOV_INST_CIT = City-level government institutions
ACT_TYPE_ORG_INDUST = Industry or business associations
ACT_TYPE_THIRD_STATE = Non-EU sovereign states (third countries)
ACT_TYPE_GOV_DIST = Districts or similar subnational units
ACT_TYPE_GOV_INST_NAT_CIT = National institutions with city-level subdivisions
ACT_TYPE_ORG_EDUC = Educational institutions (universities, schools)
ACT_TYPE_ORG_NON_PROF = Non-profit organizations (NGOs, charities)
ACT_TYPE_ORG_PROF = Professional associations
ACT_TYPE_GOV_INST_DIST = District-level government institutions
ACT_TYPE_ORG_CONS = Consumer organizations
ACT_TYPE_GOV_INST_REG = Regional-level government institutions
ACT_TYPE_GOV_REG = Regions or provinces
ACT_TYPE_GOV_OFFIC_NAT = National-level government officials
ACT_TYPE_ORG_REL = Religious organizations
ACT_TYPE_GOV_INST_NAT_REG = National institutions with regional subdivisions
ACT_TYPE_EU_DA = EU decentralized agencies
ACT_TYPE_EFTA_INST = EFTA institutions
ACT_TYPE_ORG_IO = International organizations (e.g., UN, WTO)
ACT_TYPE_GOV_OFFIC_CIT = City-level government officials
ACT_TYPE_GOV_OFFIC_UNSPEC = Government officials (level unclear)
ACT_TYPE_GOV_OFFIC_DIST = District-level government officials
ACT_TYPE_ORG_POL = Political parties or political organizations
ACT_TYPE_GOV_INST_UNSPEC = Government institutions (level unclear)
ACT_TYPE_UNSPEC = Cannot be classified with available information
ACT_TYPE_GOV_INST_REG_CIT = Regional institutions with city-level subdivisions
ACT_TYPE_EU_BODY = EU bodies (non-core institutional entities)
ACT_TYPE_EU_CB = EU corporate bodies
ACT_TYPE_EU_MISC = Other EU‑related actors not covered above


# Output Format
Respond with EXACTLY one of the codes above.
Do NOT output anything else.
"""


class EulexDBClassifyActorsTask(BaseTask):
    name = "classify_actor"
    version = "v1"
    schema = EulexDBActorSchema
    system_prompt = SYS_MSG

    def build_prompt(self, actor_name: str, context: str = "") -> str:
        return f"""
ACTOR:
{actor_name}

CONTEXT (if available):
{context}

Classify this actor.
""".strip()