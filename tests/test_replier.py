import datetime
from app.services import GenerateRepliesService
from app.core.models import (
    Review,
    Response
)

def test_replier_creates_draft(
        db,
        fake_gemini,
):
    aware = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

    with db.session_scope() as session:
        session.add(Review(
                wb_id="WB1",
                user_name="Тест",
                text="Отличный товар",
                rating=5,
                sku="111",
                created_at=aware,
                status="new",
        ))

    svc = GenerateRepliesService(
        gemini=fake_gemini,
    )
    created = svc.execute()

    assert created == 1

    with db.get_session() as session:
        resp = session.query(Response).first()
        assert resp is not None
        assert resp.status == "draft"
