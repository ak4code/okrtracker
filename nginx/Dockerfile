FROM nginx:1.27-alpine

COPY docker-entrypoint.sh /docker-entrypoint.d/40-check-local-cert.sh

RUN chmod +x /docker-entrypoint.d/40-check-local-cert.sh
