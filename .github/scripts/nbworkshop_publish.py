"""Select notebook builds and publish only their owned outputs.

Adapted from the safe-publication delivery approved in the shared conversation.
"""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import publish_outputs
from publish_outputs import git, relative_path, remote_head


def directories(config):
    folders = []
    for value in config["notebooks_dir"]:
        folder = relative_path(value.rstrip("/"))
        folders.append(folder)
    return folders


def monitored(path, folders):
    path = PurePosixPath(path)
    return path.suffix == ".ipynb" and any(folder == path or folder in path.parents for folder in folders)


def target_names(source, config):
    src = relative_path(source)
    stem = src.stem
    tutor = config["tutor_postfix"]
    student = config["student_postfix"]
    localized = re.fullmatch(r"(.+)" + re.escape(tutor) + r"(_(?:fr|en))", stem) if tutor else None
    if localized:
        stem = localized[1] + student + localized[2]
    elif tutor and stem.endswith(tutor):
        stem = stem[:-len(tutor)]
    student_path = str(src.with_name((stem if localized else stem + student) + ".ipynb"))
    zip_path = str(src.parent / "ZIP" / (src.stem + ".zip"))
    if student_path == source:
        raise ValueError(f"Student path is identical to source: {source}")
    return student_path, zip_path


def planned_changes(config, event="workflow_dispatch", before="", after="HEAD", repo=".", branch="Students"):
    folders = directories(config)
    all_files = git("ls-tree", "-r", "--name-only", "HEAD", cwd=repo).stdout.splitlines()
    current = {p for p in all_files if monitored(p, folders)}
    full = (event != "push" or bool(config.get("rebuild_all", False))
            or remote_head(branch, repo) is None or not before or set(before) == {"0"})
    changed = set()
    if event == "push" and before and set(before) != {"0"}:
        diff = git("diff", "--no-renames", "--name-only", "-z", before, after,
                   cwd=repo).stdout
        changed = {p for p in diff.split("\0") if monitored(p, folders)}
    to_convert = sorted(current if full else current & changed)
    deleted = sorted(changed - current)
    return {"convert": to_convert, "deleted": deleted, "full_rebuild": full}


def prepare_publication(config, plan, repo, summary):
    additions = {"README.md": Path(summary).resolve()}
    removals = set()
    for source in plan["convert"]:
        student, archive = target_names(source, config)
        p = Path(repo, student)
        # The module's language hook may rename the converter's normal output.
        # Standalone nbworkshop still publishes its original naming convention.
        raw_stem = Path(source).stem
        if config['tutor_postfix'] and raw_stem.endswith(config['tutor_postfix']):
            raw_stem = raw_stem[:-len(config['tutor_postfix'])]
        original_name = str(PurePosixPath(source).with_name(raw_stem + config['student_postfix'] + '.ipynb'))
        if not p.is_file() and Path(repo, original_name).is_file():
            student, p = original_name, Path(repo, original_name)
        if not p.is_file():
            raise FileNotFoundError(f"Generated student notebook missing: {p}")
        additions[student] = p.resolve()
        # Student notebooks may refer to companion assets in their metadata.
        # Publish only explicitly listed files; never mirror main wholesale.
        notebook = json.loads(p.read_text(encoding="utf-8"))
        for attached in notebook.get("metadata", {}).get("attached_files", []):
            if not isinstance(attached, str):
                raise ValueError(f"Invalid attached_files entry in {student}")
            if not attached or Path(attached).is_absolute() or "\\" in attached:
                raise ValueError(f"Invalid attached_files path in {student}: {attached!r}")
            asset = (Path(repo, student).parent / attached).resolve()
            if not asset.is_file() or not asset.is_relative_to(Path(repo).resolve()):
                raise FileNotFoundError(f"Attached notebook file unavailable: {attached!r}")
            dest_name = asset.relative_to(Path(repo).resolve()).as_posix()
            additions[dest_name] = asset
        z = Path(repo, archive)
        if config["generate_zip"]:
            if not z.is_file():
                raise FileNotFoundError(f"Generated ZIP missing: {z}")
            additions[archive] = z.resolve()
        else:
            removals.add(archive)  # Clean up a previous ZIP for a modified notebook.
    for source in plan["deleted"]:
        student, archive = target_names(source, config)
        removals.update([student, archive])
        raw_stem = PurePosixPath(source).stem
        if config['tutor_postfix'] and raw_stem.endswith(config['tutor_postfix']):
            raw_stem = raw_stem[:-len(config['tutor_postfix'])]
        removals.add(str(PurePosixPath(source).with_name(raw_stem + config['student_postfix'] + '.ipynb')))
    removals -= additions.keys()
    return additions, removals


def publish(config, plan, repo=".", summary=None, branch="Students", max_attempts=4):
    if not summary:
        raise ValueError("summary is required")
    additions, removals = prepare_publication(config, plan, repo, summary)
    return publish_outputs.publish_files(additions, removals, repo, branch, max_attempts,
                                         message="Update student notebooks")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["plan", "publish"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--plan-file", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--branch", default="Students")
    ap.add_argument("--event", default="workflow_dispatch")
    ap.add_argument("--before", default="")
    ap.add_argument("--after", default="HEAD")
    ap.add_argument("--summary")
    args = ap.parse_args()
    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    if args.action == "plan":
        result = planned_changes(config, args.event, args.before, args.after, args.repo, args.branch)
        Path(args.plan_file).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
        result = publish(config, plan, args.repo, args.summary, args.branch)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
