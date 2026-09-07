"""Behavioral fixtures for the shared-skill pre-commit gate."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / 'skills-lint.py'
SPEC = importlib.util.spec_from_file_location('skills_lint', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SkillsLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=MODULE_PATH.parents[1])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'config/skills/example'
        self.skill.mkdir(parents=True)
        self.write_skill()
        guard = self.root / "config/skills/agent-guard"
        (guard / "bin").mkdir(parents=True)
        (guard / "SKILL.md").write_text("---\nname: agent-guard\ndescription: Guard.\n---\n")
        self.executable = guard / "bin/agent-guard"
        self.executable.write_text("#!/bin/sh\nexit 0\n")
        self.executable.chmod(0o755)
        for harness in MODULE.HARNESSES:
            directory = self.root / 'config' / harness / 'skills'
            directory.mkdir(parents=True)
            (directory / 'example').symlink_to('../../skills/example')

    def write_skill(self, body='', metadata='name: example\ndescription: Example skill.'):
        (self.skill / 'SKILL.md').write_text(f'---\n{metadata}\n---\n{body}')

    def findings(self):
        return '\n'.join(MODULE.lint(self.root))

    def test_valid_resources_and_external_links(self):
        (self.skill / 'references').mkdir()
        (self.skill / 'references/a file.md').write_text('details')
        (self.skill / 'scripts').mkdir()
        (self.skill / 'scripts/check.py').write_text('')
        self.write_skill('''[details](references/a%20file.md#section)
[web](https://example.com/page) [anchor](#local)
[ref][details]
[details]: <references/a file.md>
Run `scripts/check.py`, then the `example` skill.
''', 'name: "example"\ndescription: >-\n  A multiline\n  description.')
        self.assertEqual([], MODULE.lint(self.root))

    def test_missing_metadata_and_entrypoint(self):
        for metadata in ('description: text', 'name: example', 'name: example\ndescription: ""',
                         'name: example\ndescription: >-\n'):
            with self.subTest(metadata=metadata):
                self.write_skill(metadata=metadata)
                self.assertIn('frontmatter requires', self.findings())
        self.write_skill(metadata='name: wrong\ndescription: text')
        self.assertIn('frontmatter name must be example', self.findings())
        (self.skill / 'SKILL.md').unlink()
        self.assertIn('missing SKILL.md', self.findings())

    def test_missing_inline_reference_and_script_paths(self):
        self.write_skill('''[missing](missing.md#part)
[ref]: references/missing.md
Run `scripts/missing.py`.
''')
        findings = self.findings()
        for target in ('missing.md', 'references/missing.md', 'scripts/missing.py'):
            self.assertIn(f'missing relative resource: {target}', findings)

    def test_nonportable_paths_and_unknown_skills_in_reference(self):
        (self.skill / 'details.md').write_text(
            'Path /Users/someone/code\nUse `missing-one` skill or skill `missing-two`.')
        findings = self.findings()
        self.assertIn('details.md:1: nonportable', findings)
        self.assertIn('unknown skill: missing-one', findings)
        self.assertIn('unknown skill: missing-two', findings)

    def test_required_guard_executable(self):
        self.executable.chmod(0o644)
        self.assertIn("agent-guard executable is missing or not executable", self.findings())
        self.executable.unlink()
        self.assertIn("agent-guard executable is missing or not executable", self.findings())

    def test_dangling_and_non_skill_symlinks(self):
        directory = self.root / 'config/codex/skills'
        (directory / 'dangling').symlink_to('../../skills/absent')
        (directory / 'wrong').symlink_to('../../skills')
        findings = self.findings()
        self.assertIn('skills/dangling:1: dangling', findings)
        self.assertIn('skills/wrong:1: dangling', findings)


if __name__ == '__main__':
    unittest.main()
