import os
import tempfile
import unittest

from reportlib import discover


class TestFindGitRepos(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()

    def _repo(self, rel):
        path = os.path.join(self.base, rel)
        os.makedirs(os.path.join(path, ".git"))
        return path

    def test_should_find_nested_git_repos(self):
        a = self._repo("work/alpha")
        b = self._repo("personal/beta")
        found = discover.find_git_repos([self.base])
        self.assertIn(a, found)
        self.assertIn(b, found)

    def test_should_not_descend_into_a_repo(self):
        a = self._repo("alpha")
        os.makedirs(os.path.join(a, "vendor", ".git"))
        found = discover.find_git_repos([self.base])
        self.assertIn(a, found)
        self.assertNotIn(os.path.join(a, "vendor"), found)

    def test_should_prune_node_modules(self):
        buried = os.path.join(self.base, "proj", "node_modules", "pkg")
        os.makedirs(os.path.join(buried, ".git"))
        self.assertNotIn(buried, discover.find_git_repos([self.base]))

    def test_should_respect_max_depth(self):
        deep = self._repo("a/b/c/d/e/f/g")
        self.assertNotIn(deep, discover.find_git_repos([self.base], max_depth=2))

    def test_should_detect_repo_when_dotgit_is_a_file(self):
        # worktrees and submodules use a .git file, not a directory
        path = os.path.join(self.base, "worktree")
        os.makedirs(path)
        with open(os.path.join(path, ".git"), "w", encoding="utf-8") as f:
            f.write("gitdir: /somewhere\n")
        self.assertIn(path, discover.find_git_repos([self.base]))

    def test_should_ignore_missing_search_dir(self):
        self.assertEqual(discover.find_git_repos(["/no/such/dir/anywhere"]), [])


if __name__ == "__main__":
    unittest.main()
