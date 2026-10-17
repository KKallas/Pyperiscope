import json
import threading
import urllib.request
from urllib.error import HTTPError

import pytest

from conftest import BUTTON, LABEL
from pyperiscope.cli import main
from pyperiscope.server.app import serve


@pytest.fixture
def server(project):
    srv = serve(project, "127.0.0.1", 0, token="secret")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def call(base, method, path, body=None, token="secret"):
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"X-Token": token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read())
    except HTTPError as err:
        return err.code, json.loads(err.read())


def test_token_required(server):
    assert call(server, "GET", "/api/state", token="wrong")[0] == 401
    with urllib.request.urlopen(server + "/") as res:          # the page itself loads without token
        assert b"Pyperiscope" in res.read()


def test_create_ambiguous_then_fix_with_detail(server, saved_shot):
    code, body = call(server, "POST", "/api/targets", {"name": "edit", "shot": saved_shot, "box": BUTTON(1)})
    assert code == 422 and len(body["matches"]) == 3           # refused: not unique
    code, body = call(server, "POST", "/api/targets", {"name": "edit", "shot": saved_shot, "box": BUTTON(1),
                                                       "details": [{"box": LABEL(1)}]})
    assert code == 200 and body["match"]["box"][:2] == list(BUTTON(1)[:2])
    code, body = call(server, "POST", "/api/targets/edit/test", {"shot": saved_shot})
    assert code == 200 and len(body["matches"]) == 1
    code, _ = call(server, "POST", "/api/targets", {"name": "edit", "shot": saved_shot, "box": BUTTON(1)})
    assert code == 409                                          # exists, no force
    code, state = call(server, "GET", "/api/state")
    assert [t["name"] for t in state["targets"]] == ["edit"]


def test_files_are_confined_to_project(server, saved_shot):
    req = urllib.request.Request(f"{server}/files/{saved_shot}?token=secret")
    with urllib.request.urlopen(req) as res:
        assert res.headers["Content-Type"] == "image/png"
    with pytest.raises(HTTPError) as err:
        urllib.request.urlopen(f"{server}/files/../../etc/passwd?token=secret")
    assert err.value.code in (403, 404)


def test_cli_agent_repair_flow(project, saved_shot, capsys):
    root = ["-C", str(project.root)]
    assert main(root + ["target", "create", "edit", "--shot", saved_shot, "--box", "495,215,130,55", "--force"]) == 1
    assert "3 matches" in capsys.readouterr().out
    # simulate: target saved earlier without detail, now ambiguous -> agent adds a detail
    from pyperiscope import Shot, Target
    Target.from_shot("edit", Shot.load(project.resolve(saved_shot)), BUTTON(1)).save(project.targets)
    assert main(root + ["target", "test", "edit", "--shot", saved_shot]) == 1
    result = json.loads(capsys.readouterr().out)
    index = [m["box"][1] for m in result["matches"]].index(BUTTON(2)[1])
    box = ",".join(map(str, LABEL(2)))
    assert main(root + ["target", "add-detail", "edit", "--shot", saved_shot, "--candidate", str(index), "--box", box]) == 0
    capsys.readouterr()
    assert main(root + ["target", "test", "edit", "--shot", saved_shot]) == 0
    assert json.loads(capsys.readouterr().out)["matches"][0]["box"][1] == BUTTON(2)[1]
    assert main(root + ["zoom", saved_shot if saved_shot.startswith("/") else str(project.resolve(saved_shot)),
                        "--box", "30,200,200,60"]) == 0


def test_init_scaffold(tmp_path, capsys):
    assert main(["init", str(tmp_path / "new")]) == 0
    for name in ("pyperiscope.json", "AGENTS.md", "CLAUDE.md", ".gitignore", "workflows/example_textedit.py",
                 "manual/README.md", "manual/1-limitations.md", "manual/4-qrh.md", "manual/5-dispatch.md"):
        assert (tmp_path / "new" / name).exists(), name
