FROM postgres:16
RUN apt update
RUN apt install -y libpq-dev python3 python3-poetry git sudo

WORKDIR /postxml
RUN apt install -y gcc cmake libxslt1-dev libxslt1.1 libxml2 libxml2-dev postgresql-server-dev-16
RUN echo 'postgres ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN echo a
RUN git clone https://github.com/albaike/postxml .
# RUN git checkout afee9333596330dbb8eb62113ed264b0c4c7edbf
RUN chown -R postgres:postgres .
RUN apt remove -y git

COPY docker_pstk.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/docker_pstk.sh

EXPOSE 5432
COPY docker_postgres.sh /
RUN chmod +x /docker_postgres.sh

USER postgres
WORKDIR /app
COPY pyproject.toml /app
RUN poetry install --no-root
COPY . /app
RUN poetry install
RUN echo "export POETRY_PATH=$(poetry env info --path)" > ~/poetry_path.sh
RUN chmod +x ~/poetry_path.sh

CMD ["bash", "/docker_postgres.sh"]