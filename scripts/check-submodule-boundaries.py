#!/usr/bin/env python3
"""Validate portable gitlinks and exclusive Zed/submodule ownership."""

from __future__ import annotations

import configparser
import pathlib
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE_ORG = "apostille-me"
EXPECTED_DEPENDENCIES = {
    "apostille-me/apme-clients",
    "apostille-me/apme-interfaces",
    "apostille-me/apme-libs",
    "apostille-me/apme-sync",
    "shared-auth/shared-auth-clients",
}
ALLOWED_ROLES = {
    "workspace",
    "contract",
    "sdk",
    "library",
    "synchronization",
    "tooling",
    "operations",
    "verification",
}
GITHUB_SCP = re.compile(
    r"^git@github\.com:(?P<org>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$"
)
RELATIVE_GIT = re.compile(r"^\.\.?/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$")


@dataclass(frozen=True)
class Submodule:
    name: str
    path: str
    url: str
    branch: str | None
    update: str | None


@dataclass(frozen=True)
class Policy:
    classification: str
    zed_dependency: bool
    allowed_submodule: bool


def load(path: pathlib.Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def parse_gitmodules(path: pathlib.Path) -> list[Submodule]:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    with path.open(encoding="utf-8") as handle:
        parser.read_file(handle)
    result: list[Submodule] = []
    for section in parser.sections():
        if not section.startswith('submodule "') or not section.endswith('"'):
            raise ValueError(f"invalid .gitmodules section: {section}")
        result.append(
            Submodule(
                name=section[len('submodule "') : -1],
                path=parser.get(section, "path"),
                url=parser.get(section, "url"),
                branch=parser.get(section, "branch", fallback=None),
                update=parser.get(section, "update", fallback=None),
            )
        )
    return result


def parse_inventory(path: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = raw.split("\t")
        if len(fields) != 2:
            raise ValueError(f"{path.name}:{line_number}: expected path<TAB>role")
        submodule_path, role = (field.strip() for field in fields)
        if submodule_path in result:
            raise ValueError(f"{path.name}:{line_number}: duplicate path {submodule_path}")
        if role not in ALLOWED_ROLES:
            raise ValueError(f"{path.name}:{line_number}: unsupported role {role}")
        result[submodule_path] = role
    return result


def classify(repo: str, policy: dict) -> Policy:
    for rule in policy.get("rule", []):
        suffix = str(rule.get("suffix", ""))
        if suffix and repo.endswith(suffix):
            return Policy(
                classification=str(rule.get("classification", "workspace")),
                zed_dependency=bool(rule.get("zed_dependency", False)),
                allowed_submodule=bool(rule.get("allowed_submodule", True)),
            )
    defaults = policy.get("defaults", {})
    return Policy(
        classification=str(defaults.get("classification", "workspace")),
        zed_dependency=bool(defaults.get("zed_dependency", False)),
        allowed_submodule=bool(defaults.get("allowed_submodule", True)),
    )


def portable_path(value: str) -> bool:
    path = pathlib.PurePosixPath(value)
    return (
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and "." not in path.parts
        and "\\" not in value
    )


def github_coordinate(value: str) -> str | None:
    relative = RELATIVE_GIT.fullmatch(value)
    if relative:
        return f"{PACKAGE_ORG}/{relative.group('repo')}".lower()
    scp = GITHUB_SCP.fullmatch(value)
    if scp:
        return f"{scp.group('org')}/{scp.group('repo')}".lower()
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2:
        return None
    repo = parts[1][:-4] if parts[1].endswith(".git") else parts[1]
    return f"{parts[0]}/{repo}".lower()


def gitlink_mode(path: str) -> str | None:
    result = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.split(maxsplit=1)[0]


def main() -> int:
    errors: list[str] = []
    try:
        submodules = parse_gitmodules(ROOT / ".gitmodules")
        inventory = parse_inventory(ROOT / ".zed-submodules.tsv")
        manifest = load(ROOT / ".zpkg.toml")
        policy = load(ROOT / "submodule-policy.toml")
    except (OSError, configparser.Error, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"error: invalid boundary metadata: {exc}", file=sys.stderr)
        return 1

    if policy.get("schema") != 2:
        errors.append("submodule-policy.toml must use schema = 2")
    if not submodules:
        errors.append(".gitmodules contains no submodules")

    package = manifest.get("package", {})
    dependencies = manifest.get("dependencies", {})
    if package.get("org") != PACKAGE_ORG or package.get("name") != "apme-monorepo":
        errors.append("package identity must be apostille-me/apme-monorepo")
    if package.get("repository", {}).get("url") != "https://github.com/apostille-me/apme-monorepo":
        errors.append("package.repository.url must match the canonical repository")
    if not isinstance(dependencies, dict):
        errors.append("[dependencies] must be a table")
        dependencies = {}

    dependency_names = {str(name).lower() for name in dependencies}
    for missing in sorted(EXPECTED_DEPENDENCIES - dependency_names):
        errors.append(f"missing canonical reusable dependency: {missing}")
    forbidden_dependencies = sorted(
        name for name in dependency_names if name.rsplit("/", 1)[-1].endswith(("-cli", "-infra"))
    )
    if forbidden_dependencies:
        errors.append("monorepo may not import CLI or infra packages: " + ", ".join(forbidden_dependencies))

    gitmodule_paths = {submodule.path for submodule in submodules}
    inventory_paths = set(inventory)
    for missing in sorted(gitmodule_paths - inventory_paths):
        errors.append(f"submodule missing from .zed-submodules.tsv: {missing}")
    for stale in sorted(inventory_paths - gitmodule_paths):
        errors.append(f"stale .zed-submodules.tsv entry: {stale}")

    names: set[str] = set()
    paths: set[str] = set()
    coordinates: set[str] = set()
    for submodule in submodules:
        coordinate = github_coordinate(submodule.url)
        repo = coordinate.rsplit("/", 1)[-1] if coordinate else submodule.name.rsplit("/", 1)[-1]
        expected_policy = classify(repo, policy)
        role = inventory.get(submodule.path)
        print(
            f"{submodule.path}: {coordinate or submodule.url} -> {role}; "
            f"zed_dependency={str(expected_policy.zed_dependency).lower()}"
        )

        if submodule.name in names:
            errors.append(f"duplicate submodule name: {submodule.name}")
        names.add(submodule.name)
        if submodule.path in paths:
            errors.append(f"duplicate submodule path: {submodule.path}")
        paths.add(submodule.path)
        if coordinate and coordinate in coordinates:
            errors.append(f"duplicate submodule repository: {coordinate}")
        if coordinate:
            coordinates.add(coordinate)

        if not portable_path(submodule.path):
            errors.append(f"non-portable submodule path: {submodule.path}")
        if coordinate is None:
            errors.append(f"non-portable or non-GitHub submodule URL: {submodule.url}")
        if submodule.branch == ".":
            errors.append(f"submodule {submodule.name} may not use branch = .")
        if submodule.update and (submodule.update == "command" or submodule.update.startswith("!")):
            errors.append(f"submodule {submodule.name} may not execute a custom update command")
        if gitlink_mode(submodule.path) != "160000":
            errors.append(f"submodule path is not a committed gitlink: {submodule.path}")
        if role and role != expected_policy.classification:
            errors.append(
                f"inventory role mismatch for {submodule.path}: {role} != {expected_policy.classification}"
            )
        if not expected_policy.allowed_submodule:
            errors.append(
                f"{repo} belongs on the Zed package plane and may not be a git submodule"
            )
        if coordinate and coordinate in dependency_names:
            errors.append(f"duplicate Zed/submodule ownership: {coordinate}")
        if repo.endswith(("-cli", "-infra")):
            errors.append(f"monorepo may not include CLI/infra submodule: {coordinate or repo}")

    lock_path = ROOT / ".zpkg.lock"
    if lock_path.exists():
        try:
            lock = load(lock_path)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"invalid .zpkg.lock: {exc}")
        else:
            if lock.get("version") != 1:
                errors.append(".zpkg.lock must use version = 1")
    else:
        print(".zpkg.lock is absent; resolver generation remains an explicit release prerequisite")

    status = subprocess.run(
        ["git", "submodule", "status", "--recursive"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if status.returncode != 0:
        errors.append("git submodule status --recursive failed: " + status.stderr.strip())
    for line in status.stdout.splitlines():
        if line.startswith("-"):
            errors.append("uninitialized recursive submodule: " + line[1:].strip())
        elif line.startswith("+"):
            errors.append("submodule checkout differs from committed gitlink: " + line[1:].strip())
        elif line.startswith("U"):
            errors.append("submodule has merge conflicts: " + line[1:].strip())

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        f"validated {len(submodules)} pinned workspace submodules and "
        f"{len(dependency_names)} Zed dependencies with exclusive ownership"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
