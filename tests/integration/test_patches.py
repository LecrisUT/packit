# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import git
import pytest
import shutil

from pathlib import Path
from packit.patches import PatchGenerator, PatchMetadata


@pytest.fixture
def git_repo(tmpdir):
    """
    Set up a git repo with some initial patch files in the history,
    and the same patch files updated after re-generating them from a
    source-git repo.
    """
    repo = git.Repo.init(tmpdir)
    shutil.copytree(
        src="tests/data/patches/previous/",
        dst=repo.working_tree_dir,
        dirs_exist_ok=True,
    )
    repo.git.add(repo.working_tree_dir)
    repo.git.commit("-mInitial patches")
    shutil.copytree(
        src="tests/data/patches/regenerated/",
        dst=repo.working_tree_dir,
        dirs_exist_ok=True,
    )
    return repo


def test_undo_identical(git_repo):
    """
    Check that identical patches are correctly detected and changes
    undone in the target git repo.
    """
    input_patch_list = [
        PatchMetadata(name=path.name, path=path)
        for path in Path(git_repo.working_tree_dir).iterdir()
        if path.suffix == ".patch"
    ]
    output_patch_list = [
        x for x in input_patch_list if x.name == "weird-identical.patch"
    ]
    assert (
        PatchGenerator.undo_identical(input_patch_list, git_repo) == output_patch_list
    )
    # 'weird-identical.patch' is identical, except the original patch file
    # is missing a "function" name at one of the hunks, which causes the
    # patch-ids to be different.
    # Is there any safe way to handle this?
    assert [item.a_path for item in git_repo.index.diff(None)] == [
        "weird-identical.patch"
    ]
