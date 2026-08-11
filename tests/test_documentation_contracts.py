import re
from pathlib import Path

from robot_learning.config import load_yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ENGINEERING_DOCS = (
    "dataset_pipeline.md",
    "inference_runtime.md",
    "robot_deployment.md",
    "failure_analysis.md",
    "hardware_interfaces.md",
    "dual_act_design.md",
    "deployment_checklist.md",
)
REQUIRED_RESULT_TEMPLATES = (
    "act_rollout_record_template.md",
    "dual_act_test_record_template.md",
    "deployment_record_template.md",
    "troubleshooting_record_template.md",
)


def test_engineering_documents_are_linked_from_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for filename in REQUIRED_ENGINEERING_DOCS:
        assert (ROOT / "docs" / filename).is_file()
        assert f"docs/{filename}" in readme


def test_local_markdown_links_resolve() -> None:
    markdown_files = [
        ROOT / "README.md",
        *(ROOT / "docs").glob("*.md"),
        *(ROOT / "results").glob("*.md"),
    ]
    link_pattern = re.compile(r"\[[^]]*]\(([^)]+)\)")
    broken: list[str] = []
    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.split("#", maxsplit=1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (document.parent / target).resolve().exists():
                broken.append(f"{document.relative_to(ROOT)} -> {raw_target}")
    assert not broken, "broken local Markdown links: " + ", ".join(broken)


def test_dataset_pipeline_uses_recorded_baseline_values() -> None:
    baseline = load_yaml("configs/reference/measured_experiment_baseline.yaml")
    document = (ROOT / "docs/dataset_pipeline.md").read_text(encoding="utf-8")
    numeric_document = document.replace(",", "")
    expected_values = (
        baseline["act"]["recording"]["num_episodes"],
        baseline["act"]["recording"]["dataset_fps"],
        baseline["act"]["training"]["reference_checkpoint_step"],
        baseline["smolvla_piper"]["batch_size"],
        baseline["smolvla_async"]["actions_per_chunk"],
    )
    for value in expected_values:
        assert str(value) in numeric_document


def test_documented_entrypoints_exist() -> None:
    entrypoints = (
        "scripts/check_robot_environment.sh",
        "scripts/environment_check.py",
        "scripts/setup_robot_software.sh",
        "scripts/record_piper_act.sh",
        "scripts/train_act_autodl.sh",
        "scripts/finetune_smolvla_piper.sh",
        "scripts/rollout_act_local.sh",
        "scripts/rollout_smolvla_sync.sh",
        "scripts/serve_smolvla_policy.sh",
        "scripts/open_policy_ssh_tunnel.sh",
        "scripts/run_smolvla_robot_client.sh",
        "scripts/eval_openvla_libero.sh",
        "scripts/run_dual_act.py",
    )
    for entrypoint in entrypoints:
        assert (ROOT / entrypoint).is_file(), entrypoint


def test_openvla_is_documented_as_simulation_only() -> None:
    documents = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "README.md",
            "docs/inference_runtime.md",
            "docs/robot_deployment.md",
        )
    )
    assert "OpenVLA" in documents
    assert "LIBERO" in documents
    assert "不是 Piper 真机" in documents


def test_readme_shows_the_complete_robot_learning_loop() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    architecture = readme.split("## 系统组成与架构", maxsplit=1)[1].split(
        "## 工程文档导航", maxsplit=1
    )[0]
    stages = (
        "SO-101 Leader",
        "Teleoperation",
        "Dataset Collection",
        "ACT / SmolVLA Training",
        "Checkpoint + Processors",
        "Inference Runtime",
        "Robot Interface",
        "Piper CAN",
        "Piper Robot Execution",
    )
    positions = [architecture.index(stage) for stage in stages]
    assert positions == sorted(positions)
    assert "next data iteration" in architecture


def test_hardware_interface_inventory_is_bounded() -> None:
    document = (ROOT / "docs/hardware_interfaces.md").read_text(encoding="utf-8")
    table = document.split("## 接口清单", maxsplit=1)[1].split(
        "## 数据与控制方向", maxsplit=1
    )[0]
    modules = {
        cells[0]
        for line in table.splitlines()
        if line.startswith("|")
        if (cells := [cell.strip() for cell in line.strip("|").split("|")])
        and cells[0] not in {"模块", "---"}
    }
    assert modules == {
        "SO-101 Leader",
        "Piper",
        "Front / Wrist Camera",
        "Robot PC",
        "Policy Runtime",
    }
    for unsupported_module in ("LiDAR", "IMU", "force sensor", "PLC"):
        assert unsupported_module not in document


def test_dual_act_design_matches_runtime_contract() -> None:
    document = (ROOT / "docs/dual_act_design.md").read_text(encoding="utf-8")
    required_terms = (
        "Skill A -> WAIT_CONFIRM -> Skill B",
        "skills.a.checkpoint",
        "skills.b.checkpoint",
        "preprocess",
        "postprocess",
        "policy.reset()",
        "ActionFilter",
        "allow_robot_execution=true",
        "--execute-robot",
        "失败传播",
        "多模型",
        "状态转换",
    )
    for term in required_terms:
        assert term in document


def test_deployment_checklist_covers_all_three_phases() -> None:
    document = (ROOT / "docs/deployment_checklist.md").read_text(encoding="utf-8")
    for heading in (
        "## 部署前（Pre-deployment）",
        "## 部署中（During deployment）",
        "## 部署后（Post-deployment）",
    ):
        assert heading in document
    for term in (
        "Python",
        "checkpoint",
        "preprocess/postprocess",
        "USB camera",
        "SocketCAN",
        "Dry Run",
        "MockRobot",
        "ActionFilter",
        "脱敏日志",
        "回滚",
    ):
        assert term in document


def test_failure_examples_are_not_presented_as_observations() -> None:
    document = (ROOT / "docs/failure_analysis.md").read_text(encoding="utf-8")
    assert "Troubleshooting Example" in document
    assert "Observed Failure" not in document


def test_result_templates_are_linked_and_default_to_not_verified() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    results_readme = (ROOT / "results/README.md").read_text(encoding="utf-8")
    assert "results/README.md" in readme
    assert "scripts/environment_check.py" in readme
    for filename in REQUIRED_RESULT_TEMPLATES:
        template = ROOT / "results" / filename
        assert template.is_file()
        assert filename in results_readme
        text = template.read_text(encoding="utf-8")
        assert "CONFIRMED" in text
        assert "PARTIAL_CONFIRMED" in text
        assert "NOT_VERIFIED" in text
        assert "Evidence path" in text


def test_result_templates_capture_workflow_specific_evidence() -> None:
    expected_terms = {
        "act_rollout_record_template.md": (
            "Checkpoint identifier",
            "Dataset identifier",
            "Robot action sent",
            "Sanitized command",
        ),
        "dual_act_test_record_template.md": (
            "Skill A",
            "Skill B",
            "Handoff method",
            "Failure stage",
            "Action dimension",
        ),
        "deployment_record_template.md": (
            "Pre-deployment",
            "During deployment",
            "Post-deployment",
            "Rollback",
        ),
        "troubleshooting_record_template.md": (
            "Troubleshooting Example",
            "Evidence-backed Incident",
            "Original error",
            "Root-cause status",
            "Regression test",
        ),
    }
    for filename, terms in expected_terms.items():
        text = (ROOT / "results" / filename).read_text(encoding="utf-8")
        for term in terms:
            assert term in text
