# `uot25rev` - In the Mood for Law: Sentiment Analysis of the EU Legal Order

## `valence_for_entities.py`

This file defines a binary sentiment/evaluation classifier for entity mentions. It uses a Pydantic schema with one boolean field, then a task class that gives the model a long rule-based prompt and builds input from the entity list plus the target text.

In short: output 1 if the text praises, criticizes, or otherwise evaluates the entity; output 0 if it is only factual or descriptive.

## `extract_authors_affiliations.py`

Extracts article authors and their directly linked institutional affiliations from first-page or last-page article text. The tool returns one structured author entry per author, with `affiliations` as a list so authors can have zero, one, or multiple institutional homes.

This task is meant for cases where the source text is semi-structured but not regular enough to parse reliably with regex. Author names, job titles, institutions, and credentials often appear in the same short byline or footnote, and the affiliation boundary depends on context rather than punctuation alone.

!!! example "Messy source text"

    ```text
    By E.D. Brown, Lecturer in Laws, University College London
    ```

    Structured output:

    ```json
    {
      "authors": [
        {
          "name": "E.D. Brown",
          "affiliations": ["University College London"]
        }
      ]
    }
    ```
