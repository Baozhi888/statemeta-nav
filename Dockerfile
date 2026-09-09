FROM nginx:1.27-alpine
COPY public/ /usr/share/nginx/html/
COPY nginx-container.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1