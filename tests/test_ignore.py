from resilio_companion.utils.ignore import compile_ruleset, rule_to_regex

IGNORE_RULES = [
    "*.pdf",
    "abc?.txt",
    "My Test",
    "ABC/CDE F",
    "FOO/*",
    "/FOO",
    "?recycle",
    "a/**/b",
    "b*a/**/b",
    ".git",
]
PATHS = [
    "/ABC",
    "/ABC/CDE F",
    "/123",
    "/123/ABC",
    "/123/ABC/CDE",
    "/123/ABC/CDE/Filename.pdf",
    "/FOO",
    "/FOO/QWER",
    "/a/x/y/b",
    "/alpha/x/y/b",
    "/beta/x/y/b",
    "/dosync/.sync/abcd.txt",
    "/.sync/abcd.txt",
    "/.sync/asdf.pdf",
    "/asdf/.github/asdf",
    "/.github",
]
MATCH_RESULTS = [
    False,
    True,
    False,
    False,
    False,
    True,
    True,
    True,
    True,
    False,
    True,
    True,
    False,
    False,
    False,
    False,
]


def test_rule_compiler():
    assert rule_to_regex("*.pdf") == r"/[^/]*?\.pdf"
    assert rule_to_regex("abc?.txt") == r"/abc[^/]\.txt"
    assert rule_to_regex("My Test") == "/My Test"

    assert rule_to_regex("ABC/CDE F") == "^/ABC/CDE F"
    assert rule_to_regex("FOO/*") == "^/FOO/[^/]*?"
    assert rule_to_regex("/FOO") == "^/FOO"
    assert rule_to_regex("#aopsdjif") is None


def test_ruleset_pattern():
    pattern = compile_ruleset(IGNORE_RULES)
    print(pattern)
    for p, r in zip(PATHS, MATCH_RESULTS):
        result = pattern.findall(p)
        try:
            assert (len(result) > 0) == r
        except Exception as e:
            print("Path matched wrong", p, r, result, pattern)
            raise e
