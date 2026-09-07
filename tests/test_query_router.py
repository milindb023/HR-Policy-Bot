from backend.app.query_router import route_query


def test_single_question():
    question = "How many annual leave days are employees entitled to?"

    result = route_query(question)

    assert len(result) == 1
    assert result[0] == question


def test_multi_part_question():
    question = (
        "How many annual leave days can employees carry forward, "
        "and what is the professional development stipend?"
    )

    result = route_query(question)

    assert len(result) == 2

    assert (
        "annual leave days can employees carry forward"
        in result[0].lower()
    )

    assert (
        "professional development stipend"
        in result[1].lower()
    )


def test_empty_question():
    result = route_query("")

    assert result == []