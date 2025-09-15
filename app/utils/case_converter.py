def camel_to_snake_case(tablename: str) -> str:
    chars = []

    for idx, char in enumerate(tablename):
        if idx and char.isupper():
            nxt_idx = idx + 1

            flag = nxt_idx >= len(tablename) or tablename[nxt_idx].isupper()
            prev_char = tablename[nxt_idx - 1]

            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")
        chars.append(char)

    return "".join(chars)