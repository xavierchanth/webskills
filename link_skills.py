#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from typing import Optional


def run_git(args: list[str]) -> None:
    subprocess.run(["git", *args], check=True)


def resolve_modules_path(path: str) -> str:
    if os.path.exists(path):
        return path
    if path.startswith("@") and os.path.exists(path[1:]):
        return path[1:]
    at_path = "@" + path
    if os.path.exists(at_path):
        return at_path
    return path


def ensure_submodule(path: str) -> None:
    if os.path.isdir(path) and os.listdir(path):
        return
    run_git(["submodule", "update", "--init", "--recursive", path])


def resolve_skill_path(module_path: str, skill: str) -> Optional[str]:
    candidates = [
        os.path.join(module_path, "skills", skill),
        os.path.join(module_path, skill),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def ensure_symlink(target: str, link: str) -> bool:
    if os.path.islink(link):
        os.remove(link)
    elif os.path.exists(link):
        print(f"skip: {link} exists and is not a symlink", file=sys.stderr)
        return False

    os.makedirs(os.path.dirname(link), exist_ok=True)
    rel_target = os.path.relpath(target, os.path.dirname(link))
    os.symlink(rel_target, link)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create skills symlinks from modules.json and initialize submodules",
    )
    parser.add_argument(
        "--modules",
        default="modules.json",
        help="Path to modules.json (default: modules.json)",
    )
    parser.add_argument(
        "--skills-dir",
        default="skills",
        help="Path to skills directory (default: skills)",
    )
    args = parser.parse_args()

    modules_path = resolve_modules_path(args.modules)
    if not os.path.exists(modules_path):
        print(f"modules file not found: {modules_path}", file=sys.stderr)
        return 1

    with open(modules_path, "r", encoding="utf-8") as handle:
        modules = json.load(handle)

    os.makedirs(args.skills_dir, exist_ok=True)

    created = 0
    skipped = 0
    missing = 0

    for entry in modules:
        module_path = entry.get("path")
        skills = entry.get("skills", [])
        if not module_path:
            print("skip: module entry missing path", file=sys.stderr)
            skipped += len(skills)
            continue

        try:
            ensure_submodule(module_path)
        except subprocess.CalledProcessError as exc:
            print(
                f"error: failed to init submodule {module_path}: {exc}", file=sys.stderr
            )
            skipped += len(skills)
            continue

        for skill in skills:
            target = resolve_skill_path(module_path, skill)
            if not target:
                print(
                    f"missing: {module_path} does not contain {skill}", file=sys.stderr
                )
                missing += 1
                continue
            link = os.path.join(args.skills_dir, skill)
            if ensure_symlink(target, link):
                created += 1
            else:
                skipped += 1

    print(f"links created: {created}")
    if skipped:
        print(f"links skipped: {skipped}")
    if missing:
        print(f"skills missing: {missing}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
