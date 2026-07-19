#!/usr/bin/env python3
"""Create Buttondown drafts for posts that became public in a Git push."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BUTTONDOWN_EMAILS_URL = "https://api.buttondown.com/v1/emails"
BUTTONDOWN_API_VERSION = "2026-04-01"
SITE_URL = "https://pepegar.com/"
ZERO_SHA = "0" * 40


class FrontMatterError(ValueError):
    """Raised when a post does not contain usable YAML front matter."""


@dataclass(frozen=True)
class PostDocument:
    title: str
    body: str
    draft: bool
    slug: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class PublishedPost:
    path: str
    document: PostDocument
    canonical_url: str


def parse_scalar(value: str) -> str | bool | None:
    value = value.strip()
    normalized = value.lower()
    if normalized in {"true", "yes", "on"}:
        return True
    if normalized in {"false", "no", "off"}:
        return False
    if normalized in {"null", "~"}:
        return None
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise FrontMatterError(f"Invalid quoted value: {value}") from error
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_post(content: str) -> PostDocument:
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise FrontMatterError("Post must start with YAML front matter")

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if closing_index is None:
        raise FrontMatterError("YAML front matter is missing its closing delimiter")

    values: dict[str, str | bool | None] = {}
    for line in lines[1:closing_index]:
        if not line.strip() or line.lstrip().startswith("#") or line[0].isspace():
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1).lower()] = parse_scalar(match.group(2))

    title = values.get("title")
    if not isinstance(title, str) or not title.strip():
        raise FrontMatterError("Post front matter must contain a title")

    draft = values.get("draft", False)
    if not isinstance(draft, bool):
        raise FrontMatterError("The draft field must be true or false")

    body = "".join(lines[closing_index + 1 :]).lstrip("\r\n")
    return PostDocument(
        title=title.strip(),
        body=body,
        draft=draft,
        slug=values.get("slug") if isinstance(values.get("slug"), str) else None,
        url=values.get("url") if isinstance(values.get("url"), str) else None,
    )


def became_published(before: PostDocument | None, after: PostDocument) -> bool:
    return not after.draft and (before is None or before.draft)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def canonical_url(path: str, post: PostDocument) -> str:
    if post.url:
        return urljoin(SITE_URL, post.url)

    relative_path = PurePosixPath(path).relative_to("content/posts")
    if post.slug:
        parts = (post.slug,)
    elif relative_path.name == "index.md":
        parts = relative_path.parent.parts
    else:
        parts = relative_path.with_suffix("").parts

    url_path = "/".join(filter(None, (slugify(part) for part in parts)))
    return urljoin(SITE_URL, f"posts/{url_path}/")


def run_git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        check=check,
        capture_output=True,
        text=True,
    )


def resolve_revision(revision: str) -> str:
    if revision == ZERO_SHA:
        return revision
    result = run_git("rev-parse", "--verify", f"{revision}^{{commit}}")
    return result.stdout.strip()


def empty_tree_revision() -> str:
    return run_git("hash-object", "-t", "tree", "/dev/null").stdout.strip()


def changed_post_paths(before: str, after: str) -> list[str]:
    diff_base = empty_tree_revision() if before == ZERO_SHA else before
    result = run_git(
        "diff",
        "--name-only",
        "--diff-filter=AM",
        diff_base,
        after,
        "--",
        "content/posts",
    )
    return sorted(
        path
        for path in result.stdout.splitlines()
        if PurePosixPath(path).suffix == ".md"
        and PurePosixPath(path).name != "_index.md"
    )


def file_at_revision(revision: str, path: str, *, required: bool) -> str | None:
    if revision == ZERO_SHA:
        return None
    result = run_git("show", f"{revision}:{path}", check=False)
    if result.returncode == 0:
        return result.stdout
    if required:
        raise RuntimeError(
            f"Could not read {path} at {revision}: {result.stderr.strip()}"
        )
    return None


def find_newly_published_posts(before: str, after: str) -> list[PublishedPost]:
    posts: list[PublishedPost] = []
    for path in changed_post_paths(before, after):
        after_content = file_at_revision(after, path, required=True)
        assert after_content is not None
        after_post = parse_post(after_content)
        if after_post.draft:
            print(f"Skipping draft: {path}")
            continue

        before_content = file_at_revision(before, path, required=False)
        before_post = parse_post(before_content) if before_content is not None else None
        if not became_published(before_post, after_post):
            print(f"Skipping already-published post: {path}")
            continue

        posts.append(
            PublishedPost(
                path=path,
                document=after_post,
                canonical_url=canonical_url(path, after_post),
            )
        )
    return posts


def buttondown_payload(post: PublishedPost) -> dict[str, str]:
    body = post.document.body.rstrip()
    return {
        "subject": post.document.title,
        "body": f"<!-- buttondown-editor-mode: plaintext -->\n\n{body}\n",
        "status": "draft",
        "canonical_url": post.canonical_url,
    }


def idempotency_key(path: str) -> str:
    identity = f"pepegar.com:buttondown-draft:{path}"
    return hashlib.sha256(identity.encode()).hexdigest()


def create_buttondown_draft(post: PublishedPost, api_key: str) -> str:
    request = Request(
        BUTTONDOWN_EMAILS_URL,
        method="POST",
        data=json.dumps(buttondown_payload(post)).encode(),
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "pepegar.com GitHub Actions",
            "X-API-Version": BUTTONDOWN_API_VERSION,
            "X-Idempotency-Key": idempotency_key(post.path),
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read())
    except HTTPError as error:
        response_body = error.read().decode(errors="replace")
        raise RuntimeError(
            f"Buttondown rejected {post.path} with HTTP {error.code}: {response_body}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Could not reach Buttondown for {post.path}: {error.reason}"
        ) from error

    email_id = result.get("id")
    if not isinstance(email_id, str):
        raise RuntimeError(f"Buttondown returned no email ID for {post.path}")
    return email_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, help="Commit before the push")
    parser.add_argument("--after", required=True, help="Commit after the push")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be drafted without calling Buttondown",
    )
    arguments = parser.parse_args()

    try:
        before = resolve_revision(arguments.before)
        after = resolve_revision(arguments.after)
        posts = find_newly_published_posts(before, after)

        if not posts:
            print("No posts became public in this push.")
            return 0

        api_key = os.environ.get("BUTTONDOWN_API_KEY")
        if not arguments.dry_run and not api_key:
            raise RuntimeError("BUTTONDOWN_API_KEY is not configured")

        for post in posts:
            if arguments.dry_run:
                print(
                    f"Would create draft: {post.document.title!r} "
                    f"({post.canonical_url}, {len(post.document.body)} body characters)"
                )
                continue

            assert api_key is not None
            email_id = create_buttondown_draft(post, api_key)
            print(f"Created Buttondown draft {email_id} for {post.path}")
        return 0
    except (FrontMatterError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
