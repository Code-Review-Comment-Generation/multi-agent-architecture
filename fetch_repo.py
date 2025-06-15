import subprocess
import os
import argparse


def clone_repo_and_fetch_pr(repo_name, pr_number):
    """
    Clones a GitHub repository, fetches a specific pull request,
    checks out the base of the PR, and then applies the PR patch.

    Args:
        repo_name (str): The name of the repository (e.g., 'django/django').
        pr_number (int): The pull request number.
    """
    repo_url = f"https://github.com/{repo_name}.git"
    # Use the last part of the repo_name as the directory
    clone_dir = repo_name.split('/')[-1]

    # 1. Clone the repository
    print(f"Cloning {repo_url} into ./{clone_dir}...")
    try:
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        if os.path.exists(clone_dir):
            print(
                f"Directory ./{clone_dir} might already exist. Attempting to proceed...")
        else:
            return
    except FileNotFoundError:
        print(
            "Error: Git command not found. Please ensure Git is installed and in your PATH.")
        return

    # Change directory into the cloned repo
    try:
        os.chdir(clone_dir)
    except FileNotFoundError:
        print(f"Error: Directory ./{clone_dir} not found after cloning.")
        return

    # 2. Fetch the pull request (fetches the PR's head and base)
    print(f"Fetching PR #{pr_number}...")
    pr_ref = f"pull/{pr_number}/head:pr-{pr_number}"
    # This helps in finding the base
    pr_base_ref = f"pull/{pr_number}/merge:pr-{pr_number}-merge-base"
    try:
        subprocess.run(["git", "fetch", "origin", pr_ref], check=True)
        # Fetching the merge commit can help identify the base more reliably in some cases
        # This may fail if the PR doesn't have a merge commit, so we don't use check=True
        try:
            subprocess.run(
                ["git", "fetch", "origin", f"pull/{pr_number}/merge"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Merge ref doesn't exist - this is fine, we can continue without it
            pass
        print(f"Successfully fetched PR #{pr_number}.")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching PR #{pr_number}: {e}")
        os.chdir("..")  # Go back to the original directory
        return

    # 3. Determine the base of the PR
    # The base of the PR is the commit the PR was branched from.
    # One way to get this is to look at the merge base between origin/main (or master) and the PR head.
    # However, for your request "before merging the changes of this PR",
    # we can try to get the commit just before the PR's first commit on the target branch.
    # A more direct way for "before merging" is to checkout the parent of the PR's merge commit,
    # or more simply, the target branch *before* this PR was merged.
    # For your specific request "fetch the repo before making that PR",
    # we'll checkout the commit that the PR is based on.
    try:
        # Get the hash of the PR head
        pr_head_hash_process = subprocess.run(
            ["git", "rev-parse", f"pr-{pr_number}"],
            capture_output=True, text=True, check=True
        )
        pr_head_hash = pr_head_hash_process.stdout.strip()

        # Get the merge base with a common main branch (main or master)
        # Try 'main' first, then 'master'
        main_branch_candidates = ['origin/main', 'origin/master']
        base_commit = None
        for branch_candidate in main_branch_candidates:
            try:
                # Ensure the remote branch is fetched
                subprocess.run(["git", "fetch", "origin", branch_candidate.split(
                    '/')[-1]], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                merge_base_process = subprocess.run(
                    ["git", "merge-base", branch_candidate, pr_head_hash],
                    capture_output=True, text=True, check=True
                )
                base_commit = merge_base_process.stdout.strip()
                print(
                    f"Determined base commit for PR #{pr_number} against {branch_candidate}: {base_commit}")
                break
            except subprocess.CalledProcessError:
                continue

        if not base_commit:
            # Fallback: try to get the parent of the PR's first commit if the above fails
            # This is more complex and less reliable.
            # For now, we'll rely on the merge-base. If it fails, we might be on an old Git
            # or the PR target branch is not standard.
            # A simpler approach for "before this PR" is to checkout the PR's *target branch*
            # and then apply the patch. The prompt is a bit ambiguous.
            # "fetch the repo before making that PR like before merging the changes of this PR"
            # This usually means checking out the target branch *at the commit the PR was based on*.
            # The merge-base is the best bet for this.

            # If merge-base failed, let's try to get the base from the PR itself if available via GitHub API (not done here)
            # Or, we can try to checkout the PR's *target branch* as a simpler "before" state.
            # For the given PR 19479, the target is 'main'.
            print(f"Could not reliably determine the exact base commit. Will checkout 'main' branch before applying patch.")
            # Attempt to get the default branch
            default_branch_proc = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "origin/HEAD"],
                capture_output=True, text=True, check=True
            )
            default_branch = default_branch_proc.stdout.strip().split('/')[-1]
            base_commit = default_branch  # e.g., 'main' or 'master'

        print(f"Checking out base: {base_commit}...")
        subprocess.run(["git", "checkout", base_commit], check=True)
        print(f"Checked out base '{base_commit}' successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error determining or checking out base of PR: {e}")
        os.chdir("..")
        return
    except FileNotFoundError:
        print("Error: Git command not found during base checkout.")
        os.chdir("..")
        return

    # 4. Download and apply the PR patch
    # The .diff or .patch URL for a GitHub PR is `https://github.com/{repo_name}/pull/{pr_number}.patch`
    patch_url = f"https://github.com/{repo_name}/pull/{pr_number}.patch"
    patch_file = f"pr_{pr_number}.patch"

    print(f"Downloading patch from {patch_url}...")
    try:
        # Using curl to download the patch
        subprocess.run(["curl", "-L", patch_url, "-o", patch_file], check=True)
        print(f"Patch downloaded to {patch_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading patch: {e}")
        os.chdir("..")
        return
    except FileNotFoundError:
        print("Error: curl command not found. Please ensure curl is installed.")
        os.chdir("..")
        return

    print("Applying patch...")
    try:
        # Check if the patch can be applied
        check_patch_process = subprocess.run(
            ["git", "apply", "--check", patch_file],
            capture_output=True, text=True
        )
        if check_patch_process.returncode != 0:
            print(
                f"Warning: 'git apply --check' failed. The patch may not apply cleanly.")
            print("Error details:\n", check_patch_process.stderr)
            # Ask user if they want to proceed
            proceed = input(
                "Attempt to apply the patch anyway? (y/N): ").lower()
            if proceed != 'y':
                print("Patch application aborted by user.")
                os.chdir("..")
                return

        # Apply the patch
        subprocess.run(["git", "apply", patch_file], check=True)
        print("Patch applied successfully.")
        print(
            f"\nRepository '{clone_dir}' is now at the state of '{base_commit}' with patch for PR #{pr_number} applied.")
        print("You can see the changes with 'git diff' or 'git status'.")
        print(
            "To create a branch with these changes: git checkout -b pr-{pr_number}-patched")

    except subprocess.CalledProcessError as e:
        print(f"Error applying patch: {e}")
        print("The patch might have conflicts or might have already been applied.")
        print("You can try to resolve conflicts manually or use 'git am' for more control if it's a mail-formatted patch.")
    except FileNotFoundError:
        print("Error: Git command not found during patch application.")
    finally:
        # Clean up the patch file
        if os.path.exists(patch_file):
            # os.remove(patch_file) #  Keep the patch file for inspection
            print(f"Patch file '{patch_file}' kept for inspection.")
        os.chdir("..")  # Go back to the original directory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clone a GitHub repository and apply a specific Pull Request patch."
    )
    parser.add_argument(
        "repo_name",
        help="The GitHub repository name (e.g., 'django/django')."
    )
    parser.add_argument(
        "pr_number",
        type=int,
        help="The Pull Request number."
    )

    args = parser.parse_args()

    clone_repo_and_fetch_pr(args.repo_name, args.pr_number)
