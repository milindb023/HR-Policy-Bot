from typing import List


def clean_question(question: str) -> str:
    """Clean and format a routed question."""

    question = question.strip(" ,.?")

    if not question:
        return ""

    # Capitalize the first character.
    question = question[0].upper() + question[1:]

    # Make sure it ends with a question mark.
    if not question.endswith("?"):
        question += "?"

    return question


def route_query(question: str) -> List[str]:
    """
    Detect whether a question contains multiple independent parts.

    Returns:
        A list containing one or more questions.
    """

    question = question.strip()

    if not question:
        return []

    lower_question = question.lower()

    separators = [
        " and ",
        " also ",
        " as well as ",
    ]

    for separator in separators:

        if separator in lower_question:

            parts = question.split(separator)

            cleaned_parts = [
                clean_question(part)
                for part in parts
                if part.strip()
            ]

            cleaned_parts = [
                part for part in cleaned_parts
                if part
            ]

            if len(cleaned_parts) > 1:
                return cleaned_parts

    return [clean_question(question)]


if __name__ == "__main__":

    test_questions = [
        "How many annual leave days can employees carry forward?",
        "How many annual leave days can employees carry forward, and what is the professional development stipend?",
    ]

    for question in test_questions:

        print("\nOriginal:")
        print(question)

        print("Routed questions:")

        for item in route_query(question):
            print("-", item)