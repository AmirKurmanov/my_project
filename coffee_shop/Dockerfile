FROM python:3.12-slim

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
RUN uv sync --no-cache

COPY coffee_shop/ coffee_shop/

CMD ["uv", "run", "python", "-m", "coffee_shop.main"]