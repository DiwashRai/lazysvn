
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import namedtuple
from typing import Dict, List, Tuple


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


Change = namedtuple("Change", ["status", "path"])
LogEntry = namedtuple("LogEntry", ["revision", "author", "date", "msg", "changelist"])

class SvnModel:
    def __init__(self, local_path: str, username: str, password: str):
        self._local_path = os.path.normpath(local_path)
        self._username = username
        self._password = password

        # status screen
        self._unstaged_changes: List[Change] = []
        self._added_dirs: List[Change] = []
        self._staged_changes: List[Change] = []
        self._command_log_queue: List[str] = []
        self._diff_cache = {}
        self._hide_unversioned = True

        # log screen
        self._fetched_log_entries: List[LogEntry] = []
        self._log_cache: Dict[int, Tuple[str, List[Change]]] = {}
        self._saved_msg = ""


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


    def refresh_status(self):
        self._diff_cache = {}
        self.fetch_status()


    def toggle_hide_unversioned(self):
        self._hide_unversioned = not self._hide_unversioned


    def set_saved_msg(self, msg: str):
        self._saved_msg = msg


    @property
    def saved_msg(self):
        return self._saved_msg


    def fetch_status(self):
        raw_result = self.run_command("status", ["--xml", self._local_path])
        root = ET.fromstring(raw_result)

        unstaged_changes: List[Change] = []
        added_dirs: List[Change] = []
        target = root.find("target")
        if target is not None:
            for entry in target.iter("entry"):
                path = entry.get("path", "")
                normalized_path = os.path.normpath(path)
                if normalized_path.startswith(self._local_path):
                    # +1 to remove the trailing slash
                    relative_path = normalized_path[len(self._local_path) + 1:]
                else:
                    error_msg = (
                            f"The path {path} does not start with the expected "
                            f"local path {self._local_path}.")
                    raise ValueError(error_msg)
                wc_status = entry.find("wc-status")
                status = wc_status.get("item", "") if wc_status is not None else ""

                if status == "added" and os.path.isdir(path):
                    added_dirs.append(Change(status_to_char[status], relative_path))
                    continue
                if self._hide_unversioned and status == "unversioned":
                    continue
                unstaged_changes.append(Change(status_to_char[status], relative_path))
        self._added_dirs = added_dirs
        self._unstaged_changes = unstaged_changes

        staged_changes: List[Change] = []
        for changelist in root.iter("changelist"):
            if changelist.get("name", "") == "staged":
                for entry in changelist.iter("entry"):
                    path = entry.get("path", "")
                    normalized_path = os.path.normpath(path)
                    if normalized_path.startswith(self._local_path):
                        # +1 to remove the trailing slash
                        relative_path = normalized_path[len(self._local_path) + 1:]
                    else:
                        error_msg = (
                                f"The path {path} does not start with the expected "
                                f"local path {self._local_path}.")
                        raise ValueError(error_msg)
                    wc_status = entry.find("wc-status")
                    status = wc_status.get("item", "") if wc_status is not None else ""
                    staged_changes.append(Change(status_to_char[status], relative_path))
        self._staged_changes = staged_changes


    def fetch_log(self, revision_from=None, revision_to=None, limit=100):
        args = []

        if revision_from or revision_to:
            if not revision_from:
                revision_from = "1"

            if not revision_to:
                revision_to = "HEAD"

            args += ["-r", str(revision_from) + ":" + str(revision_to)]

        if limit is not None:
            args += ["-l", str(limit)]

        args += ["--xml", "--verbose", self._local_path]
        raw_result = self.run_command("log", args)

        log_entries: List[LogEntry] = []
        root = ET.fromstring(raw_result)
        for log_entry_element in root.iter("logentry"):
            revision = log_entry_element.get("revision")
            author_element = log_entry_element.find("author")
            author = author_element.text if author_element is not None else None
            date_element = log_entry_element.find("date")
            date_text = date_element.text if date_element is not None else None
            paths_element = log_entry_element.find("paths")
            changelist: List[Change] = []
            if paths_element is not None:
                for path_element in paths_element.iter("path"):
                    action = path_element.get("action")
                    path = path_element.text
                    changelist.append(Change(action, path))

            msg_element = log_entry_element.find("msg")
            msg = msg_element.text if msg_element is not None else None

            log_entry = LogEntry(revision, author, date_text, msg, [])
            log_entries.append(log_entry)
            if revision is not None and date_text is not None:
                self._log_cache[int(revision)] = (date_text, changelist)
        self._fetched_log_entries = log_entries


    def fetch_more_logs(self, quantity) -> bool:
        revision_from = int(self._fetched_log_entries[-1].revision) - 1
        if revision_from == 0:
            return False

        revision_to = revision_from - quantity + 1
        if revision_to < 1:
            revision_to = 1

        self.fetch_log(revision_from, revision_to)
        return True


    def get_log_cache_entry(self, revision: int) -> Tuple[str, List[Change]] | None:
        return self._log_cache.get(revision, None)


    def add_file(self, rel_path: str):
        self.run_command("add", ["-N", os.path.join(self._local_path, rel_path)])


    def stage_file(self, rel_path: str):
        self.run_command("changelist", ["staged", os.path.join(self._local_path, rel_path)])


    def unstage_file(self, rel_path: str):
        self.run_command("changelist", ["--remove", os.path.join(self._local_path, rel_path)])


    def revert_file(self, rel_path: str):
        self.run_command("revert", ["-R", os.path.join(self._local_path, rel_path)])


    def diff_file(self, rel_path: str) -> str:
        if (rel_path in self._diff_cache):
            return self._diff_cache[rel_path]

        diff = self.run_command("diff", [os.path.join(self._local_path, rel_path)])
        self._diff_cache[rel_path] = diff
        return diff


    def commit_staged(self, message: str):
        if len(self._staged_changes) == 0 and len(self._added_dirs) == 0:
            raise SVNCommandError("Nothing to commit", "")

        if len(self._added_dirs) == 0:
            self.changelist_commit(message)
            return

        commit_paths = [os.path.join(self._local_path, change.path)
                        for change_list in [self._added_dirs, self._staged_changes] 
                        for change in change_list]

        self.run_command(
            "commit",
            ["--depth=empty", "-m", message] + commit_paths
        )


    def changelist_commit(self,  message: str):
        self.run_command("commit", ["--changelist", "staged", "-m", message, self._local_path])


    def is_up_to_date(self) -> bool:
        raw_result = self.run_command("status", ["-u", "--xml", self._local_path])
        root = ET.fromstring(raw_result)

        against = root.find(".//against")
        if against is None:
            return True
        head_rev = int(against.attrib["revision"])

        for entry in root.findall(".//entry"):
            wc_status = entry.find(".//wc-status")
            if wc_status and "revision" in wc_status.attrib:
                wc_rev = int(wc_status.attrib["revision"])
                if wc_rev < head_rev:
                    return False

        return True


    def run_command(self, subcommand: str, args, **kwargs):
        if subcommand != "status" and subcommand != "diff":
            self._command_log_queue.append(f"svn {subcommand} {" ".join(args)}")
        cmd = ["svn", "--non-interactive"]

        if self._username:
            cmd.append(f"--username={self._username}")

        if self._password:
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
            command = " ".join(cmd)
            if self._password and self._password in command:
                command = command.replace(self._password, "********")
            raise SVNCommandError(f"command: {command}\n\nmsg: {e.stderr}", e.stderr)

