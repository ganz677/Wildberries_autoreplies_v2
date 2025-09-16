import datetime

from sqlalchemy import select

from app.core.models import Response, Review
from app.services.publisher import PublishRepliesService


def test_publisher_publishes_draft(db, fake_wb):
    aware = datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC)

    with db.session_scope() as session:
        review = Review(
            wb_id='WB1',
            user_name='Тест',
            text='Тестовый отзыв',
            rating=5,
            sku='111',
            created_at=aware,
            status='answered',
        )
        session.add(review)
        session.flush()

        session.add(
            Response(
                review_id=review.id,
                reply_text='Черновик',
                model='fake-model',
                status='draft',
            )
        )

    svc = PublishRepliesService(wb_client=fake_wb)
    published = svc.execute()

    assert published == 1
    assert fake_wb.replies

    with db.get_session() as s:
        resp = s.execute(select(Response)).scalar_one()
        assert resp.status == 'published'
        rev = s.execute(select(Review)).scalar_one()
        assert rev.status == 'published'
