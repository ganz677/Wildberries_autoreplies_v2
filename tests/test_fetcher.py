from app.services import FetchNewReviewsService
from app.core.models import Review
from sqlalchemy import select


def test_fetcher_inserts_review(db, fake_wb):
    svc = FetchNewReviewsService(wb_client=fake_wb)
    created = svc.execute(window_days=7)

    assert created == 1

    with db.get_session() as session:
        reviews = session.execute(select(Review)).scalars().all()
        assert len(reviews) == 1
        assert reviews[0].user_name == 'Тест'