# `uot25rev` - In the Mood for Law: Sentiment Analysis of the EU Legal Order

## `valance_for_entities.py`

This file defines a binary sentiment/evaluation classifier for entity mentions. It uses a Pydantic schema with one boolean field, then a task class that gives the model a long rule-based prompt and builds input from the entity list plus the target text.

In short: output 1 if the text praises, criticizes, or otherwise evaluates the entity; output 0 if it is only factual or descriptive.
