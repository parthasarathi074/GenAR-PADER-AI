import pandas as pd


REACTION_COLUMN = (
    "patient_reaction_reactionmeddrapt"
)

OUTCOME_COLUMN = (
    "patient_reaction_reactionoutcome"
)


# --------------------------------------------------
# Known compound reaction terms
# --------------------------------------------------

COMPOUND_REACTIONS = {
    "Hallucination, visual",
    "Hallucination, auditory",
    "Hallucinations, mixed",
}


def split_reaction_values(value):
    """
    Split the comma-separated reaction field while
    preserving known reaction terms that themselves
    contain commas.
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    parts = [
        part.strip()
        for part in text.split(",")
    ]

    reactions = []

    index = 0

    while index < len(parts):

        # --------------------------------------------------
        # Check whether current part + next part form
        # a known compound reaction.
        # --------------------------------------------------

        if index + 1 < len(parts):

            candidate = (
                f"{parts[index]}, "
                f"{parts[index + 1]}"
            )

            if candidate in COMPOUND_REACTIONS:

                reactions.append(candidate)

                index += 2

                continue

        # --------------------------------------------------
        # Normal reaction
        # --------------------------------------------------

        if parts[index]:

            reactions.append(parts[index])

        index += 1

    return reactions


def split_outcome_values(value):
    """
    Split the outcome field.

    Outcomes in this dataset are comma-separated and
    do not contain the known compound comma patterns
    found in the reaction field.
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    return [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]


def normalize_reactions(row):
    """
    Convert one raw dataframe row into a list of
    normalized reaction records.

    Each reaction is paired with the outcome at the
    same position when available.

    Missing outcomes are represented as None rather
    than being invented.
    """

    reactions = split_reaction_values(
        row[REACTION_COLUMN]
    )

    outcomes = split_outcome_values(
        row[OUTCOME_COLUMN]
    )

    normalized = []

    for index, reaction in enumerate(reactions):

        outcome = (
            outcomes[index]
            if index < len(outcomes)
            else None
        )

        normalized.append(
            {
                "term": reaction,
                "outcome": outcome,
                "outcome_missing": (
                    outcome is None
                ),
            }
        )

    return normalized