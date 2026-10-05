"""CR-0: tēma "Parki un skvēri" un tēmu saraksts (tracker/CR-0.md)."""


def test_cr0_ac1_topics_list(client):
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == [
        {"code": "ROADS", "name": "Ceļi un ielas"},
        {"code": "WASTE", "name": "Atkritumi"},
        {"code": "PLANNING", "name": "Teritorijas plānošana"},
        {"code": "PARKS", "name": "Parki un skvēri"},
        {"code": "OTHER", "name": "Cits"},
    ]


def test_cr0_ac2_parks_accepted(client, valid_payload):
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201


def test_cr0_ac3_unknown_topic_rejected(client, valid_payload):
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "topic"


def test_cr0_ac4_existing_topics_unchanged(client, valid_payload):
    for code in ("ROADS", "WASTE", "PLANNING", "OTHER"):
        valid_payload["topic"] = code
        assert client.post("/submissions", json=valid_payload).status_code == 201
