FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

# Fix permissions - files need 644, directories need 755
RUN chmod 644 /usr/share/nginx/html/index.html && \
    chmod -R 755 /usr/share/nginx/html/css && \
    chmod -R 755 /usr/share/nginx/html/js && \
    find /usr/share/nginx/html/css -type f -exec chmod 644 {} \; && \
    find /usr/share/nginx/html/js -type f -exec chmod 644 {} \;

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
