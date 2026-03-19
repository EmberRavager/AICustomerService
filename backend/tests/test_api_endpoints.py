import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import routes
from main import app


class DummyTenantService:
    def __init__(self):
        self.tenants = {}
        self.configs = {}

    def create_tenant(self, name, api_key=None):
        tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
        key = api_key or f"tk_{uuid.uuid4().hex}"
        self.tenants[tenant_id] = {"name": name, "api_key": key}
        self.configs[tenant_id] = {}
        return {"tenant_id": tenant_id, "api_key": key, "name": name}

    def list_tenants(self):
        return {
            "tenants": [
                {
                    "tenant_id": tenant_id,
                    "name": data.get("name"),
                    "api_key": data.get("api_key"),
                }
                for tenant_id, data in self.tenants.items()
            ]
        }

    def get_tenant_by_key(self, api_key):
        for tenant_id, data in self.tenants.items():
            if data.get("api_key") == api_key:
                return tenant_id
        return None

    def get_tenant_config(self, tenant_id):
        return self.configs.get(tenant_id, {})

    def update_tenant_config(self, tenant_id, updates):
        current = self.configs.get(tenant_id, {})
        current.update(updates)
        self.configs[tenant_id] = current
        return current

    def update_api_key(self, tenant_id, api_key):
        if tenant_id in self.tenants:
            self.tenants[tenant_id]["api_key"] = api_key
        return {"tenant_id": tenant_id, "api_key": api_key}

    def reset_api_key(self, tenant_id):
        new_key = f"tk_{uuid.uuid4().hex}"
        if tenant_id in self.tenants:
            self.tenants[tenant_id]["api_key"] = new_key
        return {"tenant_id": tenant_id, "api_key": new_key}


class DummyKnowledgeService:
    def __init__(self, tenant_id=None):
        self.items = {}

    async def search_knowledge(self, query, limit=10, search_type="hybrid"):
        return list(self.items.values())[:limit]

    async def list_knowledge(self, category=None, limit=20, offset=0):
        items = list(self.items.values())
        if category:
            items = [item for item in items if item.get("category") == category]
        return items[offset : offset + limit]

    async def get_categories(self):
        return sorted(
            {
                item.get("category")
                for item in self.items.values()
                if item.get("category")
            }
        )

    async def add_knowledge(self, knowledge):
        item_id = knowledge.id or str(uuid.uuid4())
        payload = knowledge.dict()
        payload["id"] = item_id
        self.items[item_id] = payload
        return payload

    async def update_knowledge(self, knowledge_id, knowledge):
        payload = knowledge.dict()
        payload["id"] = knowledge_id
        self.items[knowledge_id] = payload
        return payload

    async def delete_knowledge(self, knowledge_id):
        self.items.pop(knowledge_id, None)

    async def batch_add_knowledge(self, knowledge_list):
        results = []
        for item in knowledge_list:
            item_id = item.id or str(uuid.uuid4())
            payload = item.dict()
            payload["id"] = item_id
            self.items[item_id] = payload
            results.append(payload)
        return results

    async def get_item_context(self, item_id):
        return {
            "source": "xianyu",
            "item_id": str(item_id),
            "title": "测试商品",
            "price_yuan": 9.9,
            "quantity": 5,
        }


class DummyPolicyService:
    def __init__(self, tenant_id=None):
        self.policy = {
            "auto_ship": {
                "enabled": True,
                "reply_text": "已为您安排自动发货",
                "trigger_status": ["PAID"],
            },
            "risk_guard": {"enabled": False, "blocked_keywords": []},
            "intent_routing": {"price_keywords": [], "tech_keywords": []},
            "manual_takeover": {"enabled": True},
        }

    def get_policy(self):
        return self.policy

    def update_policy(self, updates):
        self.policy.update(updates)
        return self.policy


class DummyMemoryService:
    def __init__(self, tenant_id=None):
        self.sessions = {}
        self.meta = {}
        self.history = []

    async def get_user_sessions(self, user_id=None, limit=20, offset=0):
        items = list(self.sessions.values())
        return items[offset : offset + limit]

    async def create_session(self, title=None, user_id=None):
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = {"id": session_id, "title": title or "新会话", "user_id": user_id}
        self.sessions[session_id] = session
        return session

    async def delete_session(self, session_id):
        self.sessions.pop(session_id, None)
        self.meta.pop(session_id, None)

    async def get_session_meta(self, session_id):
        return self.meta.get(session_id, {"manual_mode": False})

    async def set_manual_mode(self, session_id, enabled):
        self.meta[session_id] = {"manual_mode": enabled}
        return self.meta[session_id]

    async def save_chat_history(self, history_item):
        self.history.append(history_item)

    async def get_chat_history(self, session_id, limit=50, offset=0):
        return []

    async def clear_chat_history(self, session_id):
        return True


class DummyChatService:
    async def chat(self, request, tenant_id=None):
        return routes.ChatResponse(
            message="测试回复",
            session_id=request.session_id or "session_test",
            timestamp=datetime.now(),
            tokens_used=None,
            model_used=None,
            confidence=None,
        )

    async def chat_stream(self, request, tenant_id=None):
        yield {"delta": "测试"}

    async def get_chat_settings(self):
        return routes.ChatSettings(system_prompt=None)

    async def update_chat_settings(self, settings_update):
        return settings_update

    async def get_chat_history(self, session_id, limit, offset, tenant_id=None):
        return []

    async def clear_chat_history(self, session_id, tenant_id=None):
        return True


@pytest.fixture()
def client(monkeypatch):
    tenant_service = DummyTenantService()
    knowledge_service = DummyKnowledgeService()
    policy_service = DummyPolicyService()
    memory_service = DummyMemoryService()
    chat_service = DummyChatService()

    app.dependency_overrides[routes.get_tenant_service] = lambda: tenant_service
    app.dependency_overrides[routes.get_chat_service] = lambda: chat_service

    monkeypatch.setattr(routes, "get_chat_service", lambda: chat_service)
    monkeypatch.setattr(routes, "get_memory_service", lambda: memory_service)
    monkeypatch.setattr(routes, "get_knowledge_service", lambda: knowledge_service)
    monkeypatch.setattr(routes, "get_policy_service", lambda: policy_service)

    monkeypatch.setattr(routes, "TenantService", lambda: tenant_service)
    monkeypatch.setattr(
        routes, "KnowledgeService", lambda tenant_id=None: knowledge_service
    )
    monkeypatch.setattr(routes, "PolicyService", lambda tenant_id=None: policy_service)
    monkeypatch.setattr(routes, "MemoryService", lambda tenant_id=None: memory_service)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_tenant_lifecycle(client):
    create = client.post("/api/tenants", json={"name": "robot_a"})
    assert create.status_code == 200
    tenant_id = create.json()["data"]["tenant_id"]

    listing = client.get("/api/tenants")
    assert listing.status_code == 200
    assert listing.json()["data"]["tenants"]

    get_config = client.get(f"/api/tenants/{tenant_id}")
    assert get_config.status_code == 200

    update = client.put(
        f"/api/tenants/{tenant_id}",
        json={"model_provider": "openrouter", "model_config": {"api_key": "k"}},
    )
    assert update.status_code == 200

    reset = client.post("/api/tenants/reset-key", json={"tenant_id": tenant_id})
    assert reset.status_code == 200


def test_tenant_xianyu_config(client):
    create = client.post("/api/tenants", json={"name": "robot_b"})
    tenant_id = create.json()["data"]["tenant_id"]

    update = client.put(
        f"/api/tenants/{tenant_id}/xianyu",
        json={"cookies": "cookie_value", "seller_name": "seller", "enabled": True},
    )
    assert update.status_code == 200
    assert update.json()["data"]["has_cookies"] is True

    read_back = client.get(f"/api/tenants/{tenant_id}/xianyu")
    assert read_back.status_code == 200


def test_chat_endpoints(client):
    chat = client.post("/api/chat/", json={"message": "hello"})
    assert chat.status_code == 200
    assert chat.json()["data"]["message"] == "测试回复"

    settings = client.get("/api/chat/settings")
    assert settings.status_code == 200

    update = client.put(
        "/api/chat/settings",
        json={"model": "gpt-4", "temperature": 0.5, "max_tokens": 100},
    )
    assert update.status_code == 200


def test_memory_session_endpoints(client):
    session = client.post("/api/chat/sessions")
    assert session.status_code == 200
    session_id = session.json()["data"]["id"]

    meta = client.get(f"/api/chat/sessions/{session_id}/meta")
    assert meta.status_code == 200

    manual = client.post(
        f"/api/chat/sessions/{session_id}/manual", params={"enabled": True}
    )
    assert manual.status_code == 200

    delete = client.delete(f"/api/chat/sessions/{session_id}")
    assert delete.status_code == 200


def test_knowledge_endpoints(client):
    add = client.post(
        "/api/knowledge/",
        json={"title": "FAQ", "content": "answer", "category": "cat", "tags": []},
    )
    assert add.status_code == 200
    knowledge_id = add.json()["data"]["id"]

    listing = client.get("/api/knowledge/list")
    assert listing.status_code == 200

    categories = client.get("/api/knowledge/categories")
    assert categories.status_code == 200

    update = client.put(
        f"/api/knowledge/{knowledge_id}",
        json={"title": "FAQ", "content": "answer2", "category": "cat", "tags": []},
    )
    assert update.status_code == 200

    search = client.get("/api/knowledge/", params={"query": "FAQ"})
    assert search.status_code == 200

    batch = client.post(
        "/api/knowledge/batch",
        json=[{"title": "B1", "content": "C1", "tags": []}],
    )
    assert batch.status_code == 200

    delete = client.delete(f"/api/knowledge/{knowledge_id}")
    assert delete.status_code == 200


def test_policy_and_orders(client):
    policy = client.get("/api/policy")
    assert policy.status_code == 200

    update = client.put("/api/policy", json={"auto_ship": {"enabled": True}})
    assert update.status_code == 200

    callback = client.post(
        "/api/orders/callback",
        json={"session_id": "session_test", "status": "PAID"},
    )
    assert callback.status_code == 200


def test_model_endpoints(client):
    supported = client.get("/api/models/supported")
    assert supported.status_code == 200

    current = client.get("/api/models/current")
    assert current.status_code == 200

    listing = client.get("/api/models/list")
    assert listing.status_code == 200

    providers = client.get("/api/models/providers/openai/models")
    assert providers.status_code == 200

    invalid_provider = client.get("/api/models/providers/invalid/models")
    assert invalid_provider.status_code == 404

    status = client.get("/api/models/status")
    assert status.status_code == 200

    test = client.post("/api/models/test", json={"provider": "openrouter"})
    assert test.status_code == 200
