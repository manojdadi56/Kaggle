"""Thin clients: Jules REST, Kaggle CLI, git — all offline via injected transports."""
from orchestrator.jules_client import COMPLETED, JulesClient, session_id_of
from orchestrator.kaggle_client import KaggleClient
from orchestrator.git_ops import GitOps


# ---------- Jules ----------
class FakeHttp:
    def __init__(self):
        self.calls = []

    def __call__(self, method, url, headers, json):
        self.calls.append({"method": method, "url": url, "headers": headers, "json": json})
        if method == "POST" and url.endswith("/sessions"):
            return {"name": "sessions/abc123", "id": "abc123"}
        if "/sessions/abc123/activities" in url:
            return {"activities": [{"id": "a1", "originator": "agent"}]}
        if url.endswith("/sessions/abc123"):
            return {"name": "sessions/abc123", "state": COMPLETED,
                    "outputs": [{"pullRequest": {"url": "https://github.com/pr/1"}}]}
        if url.endswith("/sources"):
            return {"sources": [{"name": "sources/github/manojdadi56/Kaggle"}]}
        return {}


def test_jules_create_session_body_is_autonomous():
    http = FakeHttp()
    jc = JulesClient(api_key="k", http=http, source="sources/github/manojdadi56/Kaggle")
    s = jc.create_session(prompt="do x", title="T", starting_branch="main")
    assert s["id"] == "abc123"
    body = http.calls[-1]["json"]
    assert body["automationMode"] == "AUTO_CREATE_PR"
    assert body["requirePlanApproval"] is False
    assert body["sourceContext"]["source"] == "sources/github/manojdadi56/Kaggle"
    assert body["sourceContext"]["githubRepoContext"]["startingBranch"] == "main"
    assert http.calls[-1]["headers"]["X-Goog-Api-Key"] == "k"


def test_jules_get_session_terminal_and_pr_url():
    jc = JulesClient(api_key="k", http=FakeHttp())
    sess = jc.get_session("sessions/abc123")
    assert JulesClient.is_terminal(sess)
    assert JulesClient.pr_url(sess) == "https://github.com/pr/1"


def test_jules_activities_filter_cursor():
    http = FakeHttp()
    jc = JulesClient(api_key="k", http=http)
    jc.list_activities("abc123", created_after="2026-05-30T00:00:00Z")
    assert "filter=createTime>" in http.calls[-1]["url"]


def test_session_id_normalization():
    assert session_id_of("sessions/xyz") == "xyz"
    assert session_id_of("xyz") == "xyz"


# ---------- Kaggle ----------
def test_kaggle_submit_builds_cli():
    seen = {}
    def runner(cmd):
        seen["cmd"] = cmd
        return 0, "Successfully submitted"
    kc = KaggleClient(runner=runner)
    rc, out = kc.submit("nemotron", "submission.zip", "auto v1")
    assert rc == 0
    assert seen["cmd"][:4] == ["kaggle", "competitions", "submit", "nemotron"]
    assert "-f" in seen["cmd"] and "submission.zip" in seen["cmd"]


def test_kaggle_count_submissions_on_day():
    csv_out = ("fileName,date,status,publicScore\n"
               "submission.zip,2026-05-30 10:00:00,complete,0.5\n"
               "submission.zip,2026-05-30 12:00:00,complete,0.6\n"
               "submission.zip,2026-05-29 09:00:00,complete,0.4\n")
    kc = KaggleClient(runner=lambda cmd: (0, csv_out))
    assert kc.count_submissions_on("nemotron", "2026-05-30") == 2


def test_kaggle_kernels_push_parses_slug():
    kc = KaggleClient(runner=lambda cmd: (0, "Kernel pushed. ref: manojdadi56/exp1"))
    assert kc.kernels.push("kdir") == "manojdadi56/exp1"


# ---------- git ----------
def test_git_commit_all_skips_when_clean():
    log = []
    def runner(cmd, cwd):
        log.append(cmd)
        if cmd[:2] == ["git", "status"]:
            return 0, ""        # clean tree
        return 0, ""
    g = GitOps(".", runner=runner)
    rc, out = g.commit_all("msg")
    assert rc == 0 and out == "nothing to commit"
    assert ["git", "add", "-A"] in log
    assert not any(c[:2] == ["git", "commit"] for c in log)  # no commit on clean tree


def test_git_commit_all_commits_when_dirty():
    def runner(cmd, cwd):
        if cmd[:2] == ["git", "status"]:
            return 0, " M file.py"   # dirty
        return 0, "committed"
    g = GitOps(".", runner=runner)
    rc, out = g.commit_all("msg")
    assert rc == 0
