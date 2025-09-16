from .services import ReviewsPipline


if __name__ == '__main__':
    pipeline = ReviewsPipline()
    result = pipeline.run()
    print(f'Pipeline finished: {result}')