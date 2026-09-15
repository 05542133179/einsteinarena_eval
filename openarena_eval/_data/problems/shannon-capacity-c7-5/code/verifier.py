def evaluate(solution: dict) -> float:
    words = solution["words"]
    if not isinstance(words, list) or not 1 <= len(words) <= 401:
        raise ValueError("Expected between 1 and 401 words")

    checked = []
    for word in words:
        if not isinstance(word, list) or len(word) != 5:
            raise ValueError("Every word must contain exactly five coordinates")
        if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= 6 for x in word):
            raise ValueError("Word coordinates must be integers in [0, 6]")
        checked.append(tuple(word))

    if len(set(checked)) != len(checked):
        raise ValueError("Words must be distinct")

    for i, left in enumerate(checked):
        for right in checked[i + 1:]:
            if all((a - b) % 7 in (0, 1, 6) for a, b in zip(left, right)):
                raise ValueError("The submitted words are not an independent set")

    return float(len(checked))