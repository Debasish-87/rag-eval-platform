def create_project(client, name="Test Project"):
    res = client.post("/projects/", params={"name": name, "description": "desc"})
    assert res.status_code == 201
    return res.json()


def create_dataset(client, project_id, name="Test Dataset"):
    res = client.post(
        "/datasets/",
        params={
            "project_id": project_id,
            "name": name,
            "version": "1.0",
            "file_path": "app/datasets/sample_dataset.json",
        },
    )
    assert res.status_code == 201
    return res.json()


def create_experiment(client, project_id, name="Test Experiment"):
    res = client.post(
        "/experiments/",
        params={"project_id": project_id, "name": name},
    )
    assert res.status_code == 201
    return res.json()


def create_benchmark(client, experiment_id, name="Test Benchmark"):
    res = client.post(
        "/benchmarks/",
        params={"experiment_id": experiment_id, "name": name},
    )
    assert res.status_code == 201
    return res.json()


def test_root_returns_app_status(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "Running"


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_project_crud_flow(client):
    project = create_project(client, "CRUD Project")
    project_id = project["id"]

    res = client.get(f"/projects/{project_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "CRUD Project"

    res = client.put(
        f"/projects/{project_id}",
        params={"name": "Renamed Project", "description": "updated"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Renamed Project"

    res = client.get("/projects/")
    assert res.status_code == 200
    assert any(p["id"] == project_id for p in res.json())

    res = client.delete(f"/projects/{project_id}")
    assert res.status_code == 200

    res = client.get(f"/projects/{project_id}")
    assert res.status_code == 404


def test_project_not_found(client):
    res = client.get("/projects/999999")
    assert res.status_code == 404


def test_dataset_and_experiment_creation(client):
    project = create_project(client, "Pipeline Project")
    dataset = create_dataset(client, project["id"])
    experiment = create_experiment(client, project["id"])

    assert dataset["project_id"] == project["id"]
    assert experiment["project_id"] == project["id"]

    res = client.get("/datasets/")
    assert any(d["id"] == dataset["id"] for d in res.json())

    res = client.get("/experiments/")
    assert any(e["id"] == experiment["id"] for e in res.json())


def test_benchmark_status_transition(client):
    project = create_project(client, "Benchmark Project")
    experiment = create_experiment(client, project["id"])
    benchmark = create_benchmark(client, experiment["id"])

    assert benchmark["status"] == "pending"

    res = client.patch(
        f"/benchmarks/{benchmark['id']}/status",
        params={"status_value": "completed"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    res = client.get(f"/benchmarks/{benchmark['id']}")
    assert res.json()["status"] == "completed"


def test_benchmark_not_found_returns_404(client):
    res = client.get("/benchmarks/999999")
    assert res.status_code == 404


def test_summary_endpoint_reflects_created_records(client):
    before = client.get("/summary").json()

    project = create_project(client, "Summary Project")
    create_dataset(client, project["id"])
    experiment = create_experiment(client, project["id"])
    create_benchmark(client, experiment["id"])

    after = client.get("/summary").json()

    assert after["projects"] == before["projects"] + 1
    assert after["experiments"] == before["experiments"] + 1
    assert after["benchmarks"] == before["benchmarks"] + 1


def test_leaderboard_returns_ranked_list(client):
    project = create_project(client, "Leaderboard Project")
    experiment = create_experiment(client, project["id"])
    create_benchmark(client, experiment["id"], name="Leaderboard Benchmark")

    res = client.get("/leaderboard/")
    assert res.status_code == 200

    rows = res.json()
    assert isinstance(rows, list)
    ranks = [row["rank"] for row in rows]
    assert ranks == sorted(ranks)


def test_benchmark_metrics_endpoint_for_unknown_benchmark(client):
    res = client.get("/benchmarks/999999/metrics")
    assert res.status_code == 404


def test_report_download_missing_returns_404(client):
    res = client.get("/reports/999999/json")
    assert res.status_code == 404
