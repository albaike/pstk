FROM postgres:16

RUN apt update && \
    apt install -y libpq-dev python3 python3-poetry gcc cmake postgresql-server-dev-16 sudo
RUN echo 'postgres ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER postgres
WORKDIR /app
COPY pyproject.toml /app
RUN poetry install --no-root
COPY pstk /app/pstk
COPY README.md /app
RUN poetry build && \
    poetry install
RUN echo "export POETRY_PATH=$(poetry env info --path)" > ~/poetry_path.sh && \
    chmod +x ~/poetry_path.sh