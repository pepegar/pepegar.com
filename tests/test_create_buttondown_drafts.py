import contextlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from create_buttondown_drafts import (  # noqa: E402
    FrontMatterError,
    PostDocument,
    PublishedPost,
    became_published,
    buttondown_payload,
    canonical_url,
    find_newly_published_posts,
    idempotency_key,
    parse_post,
)


class ParsePostTest(unittest.TestCase):
    def test_parses_front_matter_and_strips_it_from_the_body(self):
        post = parse_post(
            """---
title: "A post: with punctuation"
draft: false
slug: custom-slug
---

Hello, **world**.
"""
        )

        self.assertEqual(post.title, "A post: with punctuation")
        self.assertFalse(post.draft)
        self.assertEqual(post.slug, "custom-slug")
        self.assertEqual(post.body, "Hello, **world**.\n")

    def test_defaults_to_published_when_draft_is_absent(self):
        post = parse_post("---\ntitle: Public post\n---\nBody\n")

        self.assertFalse(post.draft)

    def test_requires_front_matter(self):
        with self.assertRaises(FrontMatterError):
            parse_post("# Missing front matter\n")


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.published = PostDocument(title="Post", body="Body", draft=False)
        self.draft = PostDocument(title="Post", body="Body", draft=True)

    def test_new_public_post_is_published(self):
        self.assertTrue(became_published(None, self.published))

    def test_draft_becoming_public_is_published(self):
        self.assertTrue(became_published(self.draft, self.published))

    def test_edit_to_public_post_is_not_republished(self):
        self.assertFalse(became_published(self.published, self.published))

    def test_draft_stays_unpublished(self):
        self.assertFalse(became_published(self.draft, self.draft))


class PayloadTest(unittest.TestCase):
    def test_builds_a_markdown_draft_with_canonical_url(self):
        post = PublishedPost(
            path="content/posts/hello-world.md",
            document=PostDocument(title="Hello", body="Body\n", draft=False),
            canonical_url="https://pepegar.com/posts/hello-world/",
        )

        payload = buttondown_payload(post)

        self.assertEqual(payload["status"], "draft")
        self.assertEqual(payload["subject"], "Hello")
        self.assertEqual(payload["canonical_url"], post.canonical_url)
        self.assertNotIn("---", payload["body"])
        self.assertIn("buttondown-editor-mode: plaintext", payload["body"])

    def test_derives_urls_for_leaf_and_bundle_posts(self):
        post = PostDocument(title="Post", body="Body", draft=False)

        self.assertEqual(
            canonical_url("content/posts/Hello World.md", post),
            "https://pepegar.com/posts/hello-world/",
        )
        self.assertEqual(
            canonical_url("content/posts/Hello World/index.md", post),
            "https://pepegar.com/posts/hello-world/",
        )

    def test_idempotency_key_is_stable_per_post(self):
        first = idempotency_key("content/posts/hello.md")

        self.assertEqual(first, idempotency_key("content/posts/hello.md"))
        self.assertNotEqual(first, idempotency_key("content/posts/other.md"))


class GitDiscoveryTest(unittest.TestCase):
    def test_finds_publish_transition_but_not_later_edits(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            self.run_git("init", "--initial-branch=master")
            self.run_git("config", "user.name", "Test Author")
            self.run_git("config", "user.email", "test@example.com")

            post_path = Path("content/posts/hello.md")
            post_path.parent.mkdir(parents=True)
            post_path.write_text("---\ntitle: Hello\ndraft: true\n---\nDraft body\n")
            draft_revision = self.commit_all("Add draft")

            post_path.write_text(
                "---\ntitle: Hello\ndraft: false\n---\nPublished body\n"
            )
            published_revision = self.commit_all("Publish post")

            posts = find_newly_published_posts(draft_revision, published_revision)

            self.assertEqual(len(posts), 1)
            self.assertEqual(posts[0].document.title, "Hello")
            self.assertEqual(posts[0].canonical_url, "https://pepegar.com/posts/hello/")

            post_path.write_text("---\ntitle: Hello\ndraft: false\n---\nFixed typo\n")
            edited_revision = self.commit_all("Fix typo")

            self.assertEqual(
                find_newly_published_posts(published_revision, edited_revision),
                [],
            )

    def commit_all(self, message):
        self.run_git("add", ".")
        self.run_git("-c", "commit.gpgsign=false", "commit", "-m", message)
        return self.run_git("rev-parse", "HEAD").stdout.strip()

    @staticmethod
    def run_git(*arguments):
        return subprocess.run(
            ["git", *arguments],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
