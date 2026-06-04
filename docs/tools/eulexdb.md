# `eulexdb` - EULEX - EU Legal Text Data Repository

This is a collection of extraction tasks that I used for the construction of a EU Caselaw Database. Mainly, these functions solve the problem of text data where there are no regularized patterns that can be reliably used with $ReGeX$.

## `classify_actors.py`

This tool classifies actors into a standardized EulexDB actor taxonomy covering EU institutions, member states, courts, government bodies, firms, organizations, and individuals. Given an actor name and optional context, it assigns exactly one actor type, prioritizing the most specific category available. The classifier is designed for legal and institutional data extraction, with specialized rules for handling courts, government entities, and anonymized party names.

## `extract_lgts_llm.py`

Extracts litigants, party roles, and legal representatives from EU court case introductions into a structured format suitable for downstream analysis. The tool separates principals from representatives (e.g., resolving "acting on behalf of" constructions), associates lawyers with the correct litigants, and preserves the original text for auditability. It is designed for multilingual EU case law and supports complex party structures, shared representation blocks, and anonymized litigants.

## `extract_obs_llm.py`

Extracts authors of written observations and their legal representatives from EU Court of Justice case documents into a structured format. The tool distinguishes principals from representatives, resolves “acting on behalf of” constructions, and preserves the original text for traceability and manual correction. It is designed for multilingual observation sections and supports anonymized actors, shared representation blocks, and complex lawyer listings.

