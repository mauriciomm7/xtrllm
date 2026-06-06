# src/xtrllm/tasks/uot25rev/extract_authors_affiliations.py
from pydantic import BaseModel, Field

from xtrllm.core.base import BaseTask


class AuthorAffiliation(BaseModel):
    name: str = Field(..., description="Full author name in name-case capitalization.")
    affiliations: list[str] = Field(
        default_factory=list,
        description="Institutions or organizations directly linked to the author.",
    )


class ExtractAuthorsAffiliationsSchema(BaseModel):
    authors: list[AuthorAffiliation] = Field(default_factory=list)


SYS_MSG = """
You are an information extraction expert specializing in academic author bylines
and author affiliations.

# Task
Extract author names and the institutions or organizations directly linked to
each author from the provided text. The text is usually the first or last page of
an article, where author names and affiliations may appear in a byline, author
footnotes, credentials section, or short biography.

# Output requirement
Return only valid structured output matching the provided schema.
Do not return explanations, commentary, or markdown fences.

# Required structure
{
  "authors": [
    {
      "name": "Author Name",
      "affiliations": ["Institution One", "Institution Two"]
    }
  ]
}

# Rules for authors
1. Extract every author in the order they appear.
2. Extract the full name of each author, including first name and all last names.
3. Capitalize author names in name case: first letter uppercase, remaining
   letters lowercase, while preserving normal particles and punctuation when
   needed.
4. If no author is present, return an empty authors list.
5. Do not extract editors, cited scholars, judges, parties, or people merely
   mentioned in the article body unless they are presented as authors.

# Rules for affiliations
1. Extract only institutions or organizations directly linked to an author as
   that author's professional affiliation.
2. Valid affiliations include universities, research institutes, government
   ministries, law firms, courts, international or supranational courts, and
   organizations when they appear as the author's institutional home.
3. Do not extract faculties, departments, research groups, job titles, degrees,
   addresses, email domains, office locations, or biographical details that are
   not institutions.
4. Do not extract organizations merely mentioned in article content.
5. If an author has no affiliation in the text, use an empty affiliations list.
6. If one affiliation applies to multiple authors, include it for each linked
   author.
7. Standardize institution names when the source gives a well-known variant:
   - Leyden -> Leiden
   - Universita di Bologna -> University of Bologna
   - Rijksuniversiteit Groningen -> University of Groningen
   - Universitat Wien -> University of Vienna
8. Translate well-known institution names to English when the intended
   institution is clear.

# Examples
Text: "By E.D. Brown, Lecturer in Laws, University College London"
Output:
{
  "authors": [
    {"name": "E.D. Brown", "affiliations": ["University College London"]}
  ]
}

Text: "Katarzyna ZIELESKIEWICZ and BARTLOMIEJ KURCZ"
Output:
{
  "authors": [
    {"name": "Katarzyna Zieleskiewicz", "affiliations": []},
    {"name": "Bartlomiej Kurcz", "affiliations": []}
  ]
}

Text: "Marc Blanquet, Professor of European Law, Rijksuniversiteit Groningen; Barrister, Cleary Gottlieb Steen & Hamilton"
Output:
{
  "authors": [
    {
      "name": "Marc Blanquet",
      "affiliations": [
        "University of Groningen",
        "Cleary Gottlieb Steen & Hamilton"
      ]
    }
  ]
}

Text: "The Commission approved the decision..."
Output:
{
  "authors": []
}
"""


class ExtractAuthorsAffiliationsTask(BaseTask):
    name = "extract_authors_affiliations"
    version = "v1"
    schema = ExtractAuthorsAffiliationsSchema
    system_prompt = SYS_MSG

    def build_prompt(self, text: str) -> str:
        return f"""
TEXT:
{text}

Extract all authors and their directly linked affiliations.
""".strip()
