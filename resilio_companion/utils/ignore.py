import re
from typing import Optional


def rule_to_regex(rule: str) -> Optional[str]:
    rule = rule.replace("\\", "/")
    rule = rule.split("#")[0]

    if len(rule) == 0:
        return None

    # Escape special characters
    rule = re.sub("([.+$^])", r"\\\1", rule)

    # "If an ignore filter consists of 2 components, it will be applied to the root of a sync folder."
    if "/" in rule:
        if not rule.startswith("/"):
            rule = "/" + rule
        rule = "^" + rule
    else:
        # We're matching a single part of a path, add a / to force it to match from the start of a part's string
        rule = "/" + rule + "(/|$)"

    # Question marks can be any single character but the path deliminator
    rule = re.sub(r"\?", "[^/]", rule)

    # Replace single stars with wildcards that cannot transcend paths
    rule = re.sub(r"((?<!\*)\*(?!\*))", "[^/]*?", rule)

    # Replace double stars with wildcards that can transcend paths
    rule = re.sub(r"\*\*", ".*?", rule)

    return rule


def compile_ruleset(rules: list[str]) -> re.Pattern:
    """
    Given a list of rules from a Resilio Ignore file, return a Regex pattern that will match ignore file paths.
    Paths should start with a / and use the forward slash (/) as a path delimiter.

    """
    patterns = [rule_to_regex(r) for r in rules]
    rules_pattern = "|".join([p for p in patterns if p])
    return re.compile(f"(?<!^/.sync)({rules_pattern})")


def rules_to_set(rules: list[str]) -> set:
    rule_set = set()

    for r in rules:
        r = r.split("#")[0]
        r = r.strip()
        if r:
            rule_set.add(r)

    return rule_set
