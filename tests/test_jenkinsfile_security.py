"""
Tests property-based (Hypothesis) pour la sécurité des pipelines Jenkins.
Analyse statique du contenu des 8 Jenkinsfiles du projet CMV.

Feature: jenkins-pipeline-security
"""
import os
import re
from pathlib import Path

from hypothesis import given, settings, assume
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

JENKINSFILE_NAMES = [
    "Jenkins-gateway",
    "Jenkins-gateway-cdk",
    "Jenkinsfile-gateway-exemple",
    "Jenkins-chambres",
    "Jenkins-chambres-cdk",
    "Jenkins-patients",
    "Jenkins-ml",
    "Jenkins-ml-cdk",
]

# Known secret-related variable names used across the Jenkinsfiles
SECRET_VAR_NAMES = [
    "DOCKER_USER",
    "DOCKER_PASS",
    "DOCKERHUB_CREDENTIALS_USR",
    "DOCKERHUB_CREDENTIALS_PSW",
    "EC2_HOST",
    "EC2_USER",
    "EC2_SERVER",
    "GATEWAY_HOST",
    "GATEWAY_USER",
    "CHAMBRES_HOST",
    "CHAMBRES_USER",
    "PATIENTS_HOST",
    "PATIENTS_USER",
    "ML_HOST",
    "ML_USER",
    "SSH_CREDENTIALS",
]


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

# Strategy: valid shell variable names (letters, digits, underscores)
st_variable_names = st.from_regex(r"[A-Z][A-Z0-9_]{2,20}", fullmatch=True)

# Strategy: Docker image names like "org/repo"
st_image_names = st.builds(
    lambda org, repo: f"{org}/{repo}",
    org=st.from_regex(r"[a-z][a-z0-9]{2,12}", fullmatch=True),
    repo=st.from_regex(r"[a-z][a-z0-9_]{2,12}", fullmatch=True),
)

# Strategy: host names (simple DNS-like)
st_host_names = st.builds(
    lambda sub, domain, tld: f"{sub}.{domain}.{tld}",
    sub=st.from_regex(r"[a-z][a-z0-9]{1,8}", fullmatch=True),
    domain=st.from_regex(r"[a-z][a-z0-9]{2,10}", fullmatch=True),
    tld=st.sampled_from(["com", "io", "net", "org", "fr"]),
)

# Strategy: pick one of the known secret variable names
st_secret_names = st.sampled_from(SECRET_VAR_NAMES)

# Strategy: pick one of the 8 Jenkinsfile names
st_jenkinsfile_names = st.sampled_from(JENKINSFILE_NAMES)


# ---------------------------------------------------------------------------
# Helper: read Jenkinsfile contents
# ---------------------------------------------------------------------------

def read_jenkinsfile(name: str) -> str:
    """Read the content of a Jenkinsfile by name from the workspace root."""
    path = WORKSPACE_ROOT / name
    if not path.exists():
        raise FileNotFoundError(f"Jenkinsfile not found: {path}")
    return path.read_text(encoding="utf-8")


def read_all_jenkinsfiles() -> dict[str, str]:
    """Return a dict mapping Jenkinsfile name -> content for all 8 files."""
    return {name: read_jenkinsfile(name) for name in JENKINSFILE_NAMES}


# ---------------------------------------------------------------------------
# Helper: parse sh blocks
# ---------------------------------------------------------------------------

def parse_sh_blocks(content: str) -> list[str]:
    """
    Extract all sh block bodies from a Jenkinsfile.

    Matches both single-quoted (sh '''...''') and double-quoted (sh \"\"\"...\"\"\")
    sh blocks, as well as single-line sh 'cmd' / sh "cmd" forms.
    """
    blocks: list[str] = []

    # Triple-quoted blocks: sh ''' ... ''' or sh \"\"\" ... \"\"\"
    for pattern in [
        r"sh\s+'''(.*?)'''",
        r'sh\s+"""(.*?)"""',
    ]:
        for m in re.finditer(pattern, content, re.DOTALL):
            blocks.append(m.group(1))

    # Single-line: sh 'cmd' or sh "cmd"
    for pattern in [
        r"sh\s+'([^']*)'",
        r'sh\s+"([^"]*)"',
    ]:
        for m in re.finditer(pattern, content):
            # Skip if this is part of a triple-quoted block already captured
            body = m.group(1)
            if body not in blocks:
                blocks.append(body)

    return blocks


# ---------------------------------------------------------------------------
# Helper: parse environment block
# ---------------------------------------------------------------------------

def parse_environment_block(content: str) -> str | None:
    """
    Extract the environment { ... } block from a Jenkinsfile.

    Returns the text inside the braces, or None if not found.
    Uses brace-counting to handle nested braces.
    """
    match = re.search(r'\benvironment\s*\{', content)
    if not match:
        return None

    start = match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1

    return content[start:i - 1]


# ---------------------------------------------------------------------------
# Helper: parse post block
# ---------------------------------------------------------------------------

def parse_post_block(content: str) -> str | None:
    """
    Extract the post { ... } block from a Jenkinsfile.

    Returns the text inside the braces, or None if not found.
    Uses brace-counting to handle nested braces.
    """
    # Match 'post' at the pipeline level (not inside a string)
    match = re.search(r'\bpost\s*\{', content)
    if not match:
        return None

    start = match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1

    return content[start:i - 1]


def parse_post_always_block(content: str) -> str | None:
    """
    Extract the always { ... } sub-block from the post block.
    """
    post = parse_post_block(content)
    if post is None:
        return None

    match = re.search(r'\balways\s*\{', post)
    if not match:
        return None

    start = match.end()
    depth = 1
    i = start
    while i < len(post) and depth > 0:
        if post[i] == '{':
            depth += 1
        elif post[i] == '}':
            depth -= 1
        i += 1

    return post[start:i - 1]


# ---------------------------------------------------------------------------
# Helper: detect heredoc patterns
# ---------------------------------------------------------------------------

def find_heredocs(content: str) -> list[dict]:
    """
    Find all heredoc patterns in a Jenkinsfile.

    Returns a list of dicts with keys:
      - 'delimiter': the heredoc delimiter (e.g. 'EOF')
      - 'quoted': True if the delimiter is quoted (<< 'EOF'), False otherwise
      - 'body': the heredoc body text
      - 'start': start position in content
    """
    results: list[dict] = []

    # Match << 'DELIM' (quoted) or << DELIM (unquoted)
    pattern = r"<<\s*(?:'([A-Z_]+)'|\"([A-Z_]+)\"|([A-Z_]+))"
    for m in re.finditer(pattern, content):
        quoted_single = m.group(1)
        quoted_double = m.group(2)
        unquoted = m.group(3)

        if quoted_single:
            delimiter = quoted_single
            quoted = True
        elif quoted_double:
            delimiter = quoted_double
            quoted = True
        else:
            delimiter = unquoted
            quoted = False

        # Find the heredoc body (from after the delimiter line to the closing delimiter)
        body_start = m.end()
        closing_pattern = re.compile(r'^\s*' + re.escape(delimiter) + r'\s*$', re.MULTILINE)
        closing_match = closing_pattern.search(content, body_start)
        body = content[body_start:closing_match.start()] if closing_match else ""

        results.append({
            "delimiter": delimiter,
            "quoted": quoted,
            "body": body,
            "start": m.start(),
        })

    return results


# ---------------------------------------------------------------------------
# Helper: detect withCredentials blocks
# ---------------------------------------------------------------------------

def find_with_credentials_blocks(content: str) -> list[str]:
    """
    Find all withCredentials(...) { ... } blocks in a Jenkinsfile.

    Returns a list of the block bodies (text inside the outer braces).
    """
    results: list[str] = []

    # Find each withCredentials( ... ) { ... }
    for m in re.finditer(r'\bwithCredentials\s*\(', content):
        # Skip to the closing paren of the argument list
        paren_start = m.end() - 1  # position of '('
        depth = 1
        i = paren_start + 1
        while i < len(content) and depth > 0:
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
            i += 1
        # i is now just after the closing ')'

        # Find the opening brace of the block
        brace_match = re.search(r'\{', content[i:])
        if not brace_match:
            continue

        block_start = i + brace_match.end()
        depth = 1
        j = block_start
        while j < len(content) and depth > 0:
            if content[j] == '{':
                depth += 1
            elif content[j] == '}':
                depth -= 1
            j += 1

        results.append(content[block_start:j - 1])

    return results


def find_with_credentials_credential_ids(content: str) -> list[str]:
    """
    Extract all credentialsId values from withCredentials blocks.
    """
    return re.findall(r"credentialsId\s*:\s*['\"]([^'\"]+)['\"]", content)


# ---------------------------------------------------------------------------
# Smoke tests — verify helpers work on real Jenkinsfiles
# ---------------------------------------------------------------------------

def test_all_jenkinsfiles_readable():
    """All 8 Jenkinsfiles can be read from the workspace root."""
    files = read_all_jenkinsfiles()
    assert len(files) == 8
    for name, content in files.items():
        assert len(content) > 0, f"{name} is empty"
        assert "pipeline" in content, f"{name} does not look like a Jenkinsfile"


def test_parse_sh_blocks_returns_list():
    """parse_sh_blocks returns a non-empty list for each Jenkinsfile."""
    for name, content in read_all_jenkinsfiles().items():
        blocks = parse_sh_blocks(content)
        assert isinstance(blocks, list), f"{name}: expected list"
        assert len(blocks) > 0, f"{name}: no sh blocks found"


def test_parse_environment_block_returns_string():
    """parse_environment_block returns a non-None string for each Jenkinsfile."""
    for name, content in read_all_jenkinsfiles().items():
        env_block = parse_environment_block(content)
        assert env_block is not None, f"{name}: no environment block found"
        assert isinstance(env_block, str)


def test_parse_post_block_returns_string():
    """parse_post_block returns a non-None string for each Jenkinsfile."""
    for name, content in read_all_jenkinsfiles().items():
        post_block = parse_post_block(content)
        assert post_block is not None, f"{name}: no post block found"
        assert isinstance(post_block, str)


def test_find_heredocs_returns_list():
    """find_heredocs returns a list for each Jenkinsfile."""
    for name, content in read_all_jenkinsfiles().items():
        heredocs = find_heredocs(content)
        assert isinstance(heredocs, list), f"{name}: expected list"


def test_find_with_credentials_blocks_returns_list():
    """find_with_credentials_blocks returns a non-empty list for each Jenkinsfile."""
    for name, content in read_all_jenkinsfiles().items():
        blocks = find_with_credentials_blocks(content)
        assert isinstance(blocks, list), f"{name}: expected list"
        assert len(blocks) > 0, f"{name}: no withCredentials blocks found"

