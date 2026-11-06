import pytest
import app as appmod


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(appmod, "DB_PATH", str(tmp_path / "teste.db"))
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client()


def login(client):
    return client.post("/login", data={"usuario": appmod.APP_USER, "senha": appmod.APP_PASSWORD})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.get_json()["status"] == "ok"


def test_exige_login(client):
    r = client.get("/")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_login_invalido(client):
    r = client.post("/login", data={"usuario": "x", "senha": "y"})
    assert "inválidos" in r.get_data(as_text=True)


def test_adicionar_chamado(client):
    login(client)
    client.post("/add", data={"numero": "1001", "titulo": "Implantação Cliente A", "status": "Aberto"})
    assert "Implantação Cliente A" in client.get("/").get_data(as_text=True)


def test_chamado_duplicado(client):
    login(client)
    d = {"numero": "1001", "titulo": "A", "status": "Aberto"}
    client.post("/add", data=d)
    client.post("/add", data=d)
    assert "já existe" in client.get("/").get_data(as_text=True)


def test_concluir_preenche_data(client):
    login(client)
    client.post("/add", data={"numero": "1", "titulo": "T", "status": "Aberto"})
    client.post("/update/1", data={"status": "Concluído"})
    assert appmod.date.today().isoformat() in client.get("/").get_data(as_text=True)


def test_exportar_csv(client):
    login(client)
    client.post("/add", data={"numero": "7", "titulo": "Teste CSV", "status": "Aberto"})
    r = client.get("/export.csv")
    assert r.mimetype == "text/csv" and "Teste CSV" in r.get_data(as_text=True)
