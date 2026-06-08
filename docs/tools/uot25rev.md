# `uot25rev` - In the Mood for Law: Sentiment Analysis of the EU Legal Order

## `valence_for_entities.py`

This file defines a binary sentiment/evaluation classifier for entity mentions. It uses a Pydantic schema with one boolean field, then a task class that gives the model a long rule-based prompt and builds input from the entity list plus the target text.

In short: output 1 if the text praises, criticizes, or otherwise evaluates the entity; output 0 if it is only factual or descriptive.

!!! example "Evaluative sentence"

    ```text
    Entities: THE COMMISSION
    Text: In accordance with Article 89 THE COMMISSION had the duty to ensure that the principles laid down in Articles 85 and 86 were put into effect, but it was only given the power to investigate the cases that were brought before it and suggest suitable remedies, so that if the infringement continued THE COMMISSION would confirm the existence of the infringement by means of a reasoned decision and authorise the member states to take the necessary measures to remedy the situation.

    ```

    Structured output:

    ```json
    {
      "label": true
    }
    ```

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
