from app.services import ReviewsPipeline


def test_pipeline_end_to_end(
    db,  # noqa: ARG001
    fake_wb,
    fake_gemini,
    monkeypatch,  # noqa: ARG001
):
    pipeline = ReviewsPipeline()
    pipeline.fetcher.wb_client = fake_wb
    pipeline.replier.gem = fake_gemini
    pipeline.publisher.wb = fake_wb

    result = pipeline.run()

    assert result['fetched_reviews'] == 1
    assert result['drafted_responses'] == 1
    assert result['published_responses'] == 1
    assert fake_wb.replies
