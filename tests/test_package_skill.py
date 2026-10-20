"""Tests for tools/package_skill.py: the archive must not depend on the platform that builds it.

Path ordering ignores case on Windows and zipfile marks Windows-built entries as MS-DOS, so an archive built
on Windows used to differ from the one CI builds on Linux. The suite runs on both, so these tests would have
caught it.
"""
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as h  # noqa: E402

package = h.load_script("tools/package_skill.py")


class PackageCase(h.TempDirCase):
    def skill(self):
        skill = self.tmp / "skills" / "demo-skill"
        h.write(skill, "SKILL.md", "---\nname: demo-skill\n---\n# Demo\n")
        h.write(skill, "assets/skeleton.md", "# Skeleton\n")
        h.write(skill, "references/Guide.md", "# Guide\n")
        h.write(skill, "references/api.md", "# Api\n")
        h.write(skill, "scripts/run.py", "print('x')\n")
        return skill

    def test_entries_are_in_case_sensitive_path_order(self):
        archive, _ = package.build(self.skill(), self.tmp / "out")
        names = zipfile.ZipFile(str(archive)).namelist()
        self.assertEqual(names, sorted(names))
        self.assertEqual(names[0], "demo-skill/SKILL.md")

    def test_entry_headers_do_not_depend_on_the_platform(self):
        archive, _ = package.build(self.skill(), self.tmp / "out")
        for info in zipfile.ZipFile(str(archive)).infolist():
            self.assertEqual(info.create_system, 3, info.filename)
            self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0), info.filename)
            self.assertEqual(info.external_attr >> 16, 0o644, info.filename)

    def test_two_builds_are_identical_and_the_twin_is_the_same_archive(self):
        first, twin = package.build(self.skill(), self.tmp / "a")
        second, _ = package.build(self.skill(), self.tmp / "b")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(first.read_bytes(), twin.read_bytes())


if __name__ == "__main__":
    unittest.main()
