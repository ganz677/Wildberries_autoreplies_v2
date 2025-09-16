from app.services import ReviewsPipline


def test_pipeline_end_to_end(
        db,
        fake_wb,
        fake_gemini,
        monkeypatch,
):
    pipeline = ReviewsPipline()
    pipeline.fetcher.wb_client = fake_wb
    pipeline.replier.gem = fake_gemini
    pipeline.publisher.wb = fake_wb

    result = pipeline.run()

    assert result["fetched_reviews"] == 1
    assert result["drafted_responses"] == 1
    assert result["published_responses"] == 1
    assert fake_wb.replies