
import os
import subprocess
import xml.etree.ElementTree as ET
from typing import List


char_to_status = {
    "A": "added",
    "C": "conflicted",
    "D": "deleted",
    "I": "ignored",
    "M": "modified",
    "R": "replaced",
    "X": "external",   # an unversioned directory created by an externals definition
    "?": "unversioned",
    "!": "missing",    # item is missing (removed by non-svn command) or incomplete
    "~": "obstructed", # versioned item obstructed by some item of a different kind
}


status_to_char = {v: k for k, v in char_to_status.items()}


class SVNCommandError(Exception):
    def __init__(self, message, stderr):
        super().__init__(message)
        self.stderr = stderr


class Changes:
    def __init__(self, path: str, status: str):
        self._path: str = path
        self._status: str = status


    @property
    def path(self) -> str:
        return self._path


    @property
    def status(self) -> str:
        return self._path


class SvnModel:
    def __init__(self, local_path: str, username: str, password: str):
        self._local_path = local_path
        self._username = username
        self._password = password

        self._unstaged_changes: List[Changes] = []
        self._added_dirs: List[Changes] = []
        self._staged_changes: List[Changes] = []
        self._command_log_queue: List[str] = []
        self._diff_cache = {}
        self._hide_unversioned = True


    @property
    def unstaged_changes(self):
        return self._unstaged_changes


    @property
    def staged_changes(self):
        return self._staged_changes


    @property
    def command_log_queue(self):
        return self._command_log_queue


    def clear_command_log_queue(self):
        self._command_log_queue = []


    def refresh(self):
        self._diff_cache = {}
        self.fetch_status()


    def toggle_hide_unversioned(self):
        self._hide_unversioned = not self._hide_unversioned


    def fetch_status(self):
        raw_result = self.run_command("status", ["--xml", self._local_path])
        root = ET.fromstring(raw_result)

        unstaged_changes: List[Changes] = []
        added_dirs: List[Changes] = []
        target = root.find("target")
        if target is not None:
            for entry in target.findall("entry"):
                path = entry.get("path", "")
                relative_path = path[len(self._local_path):]
                wc_status = entry.find("wc-status")
                status = wc_status.get("item", "") if wc_status is not None else ""
                if status == "added" and os.path.isdir(path):
                    added_dirs.append(Changes(relative_path, status_to_char[status]))
                    continue
                if self._hide_unversioned and status == "unversioned":
                    continue
                unstaged_changes.append(Changes(relative_path, status_to_char[status]))
        self._added_dirs = added_dirs
        self._unstaged_changes = unstaged_changes

        staged_changes: List[Changes] = []
        for changelist in root.findall("changelist"):
            name = changelist.get("name", "")
            if (name == "staged"):
                for entry in changelist.findall("entry"):
                    path = entry.get("path", "")
                    relative_path = path[len(self._local_path):]
                    wc_status = entry.find("wc-status")
                    status = wc_status.get("item", "") if wc_status is not None else ""
                    staged_changes.append(Changes(relative_path, status_to_char[status]))
        self._staged_changes = staged_changes


    def add_file(self, rel_path: str):
        self.run_command("add", ["-N", self._local_path + rel_path])


    def stage_file(self, rel_path: str):
        self.run_command("changelist", ["staged", self._local_path + rel_path])


    def unstage_file(self, rel_path: str):
        self.run_command("changelist", ["--remove", self._local_path + rel_path])


    def revert_file(self, rel_path: str):
        self.run_command("revert", ["-R", self._local_path + rel_path])


    def diff_file(self, rel_path: str) -> str:
        if (rel_path in self._diff_cache):
            return self._diff_cache[rel_path]

        diff = self.run_command("diff", [self._local_path + rel_path])
        self._diff_cache[rel_path] = diff
        return diff


    def commit_staged(self, message: str):
        if len(self._staged_changes) == 0 and len(self._added_dirs) == 0:
            raise SVNCommandError("Nothing to commit", "")

        if len(self._added_dirs) == 0:
            self.changelist_commit(message)
            return

        commit_paths = [self._local_path + change.path
                        for change_list in [self._added_dirs, self._staged_changes] 
                        for change in change_list]

        self.run_command(
            "commit",
            ["--depth=empty", "-m", message] + commit_paths
        )


    def changelist_commit(self,  message: str):
        self.run_command("commit", ["--changelist", "staged", "-m", f"\"{message}\"", self._local_path])


    def is_up_to_date(self) -> bool:
        raw_result = self.run_command("status", ["-u", "--xml", self._local_path])
        root = ET.fromstring(raw_result)

        against = root.find(".//against")
        if against is None:
            return True
        head_rev = int(against.attrib['revision'])

        for entry in root.findall('.//entry'):
            wc_status = entry.find(".//wc-status")
            if wc_status and 'revision' in wc_status.attrib:
                wc_rev = int(wc_status.attrib['revision'])
                if wc_rev < head_rev:
                    return False

        return True


    def run_command(self, subcommand: str, args, **kwargs):
        cmd = ["svn", "--non-interactive"]

        if self._username:
            cmd.append(f"--username={self._username}")

        if self._password:
            cmd.append(f"--password={self._password}")

        cmd += [subcommand] + args
        if subcommand != "status" and subcommand != "diff":
            self._command_log_queue.append(" ".join(cmd))
        return self.external_command(cmd, **kwargs)


    def external_command(self, cmd) -> str:
        try:
            result = subprocess.run(
                    cmd, 
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            command = " ".join(cmd)
            if self._password and self._password in command:
                command = command.replace(self._password, "********")
            raise SVNCommandError(f"command: {command}\n\nmsg: {e.stderr}", e.stderr)

