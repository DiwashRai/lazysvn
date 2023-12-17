
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
        self._staged_changes: List[Changes] = []


    @property
    def unstaged_changes(self):
        return self._unstaged_changes


    @property
    def staged_changes(self):
        return self._staged_changes


    def fetch_status(self):
        raw_result = self.run_command("status", ["--xml", self._local_path])
        root = ET.fromstring(raw_result)

        unstaged_changes: List[Changes] = []
        target = root.find("target")
        if (target is not None):
            for entry in target.findall("entry"):
                path = entry.get("path", "")
                wc_status = entry.find("wc-status")
                status = wc_status.get("item", "") if wc_status is not None else ""
                unstaged_changes.append(Changes(path, status_to_char[status]))
        self._unstaged_changes = unstaged_changes

        staged_changes: List[Changes] = []
        for changelist in root.findall("changelist"):
            name = changelist.get("name", "")
            if (name == "staged"):
                for entry in changelist.findall("entry"):
                    path = entry.get("path", "")
                    wc_status = entry.find("wc-status")
                    status = wc_status.get("item", "") if wc_status is not None else ""
                    staged_changes.append(Changes(path, status_to_char[status]))
        self._staged_changes = staged_changes


    def add_file(self, file_path: str):
        self.run_command("add", [file_path])


    def stage_file(self, file_path: str):
        self.run_command("changelist", ["staged", file_path])


    def unstage_file(self, file_path: str):
        self.run_command("changelist", ["--remove", file_path])


    def revert_file(self, file_path: str):
        self.run_command("revert", [file_path])


    def run_command(self, subcommand: str, args, **kwargs):
        cmd = ["svn", "--non-interactive"]

        if (self._username):
            cmd.append(f"--username={self._username}")

        if (self._password):
            cmd.append(f"--password={self._password}")

        cmd += [subcommand] + args
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
            print(f"Error occurred: {e.stderr}")
            return ""
