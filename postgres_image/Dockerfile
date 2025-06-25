FROM --platform=linux/amd64  postgres:17.4-bookworm

# Add packages for configuration locales
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/*

# Generate new locale (ru_RU)
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8

# Set env for new locale
ENV LANG ru_RU.utf8
