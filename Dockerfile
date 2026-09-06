FROM ubuntu:24.04

# Install dependencies in a single layer so a failed/retried install doesn't
# leave a stale apt cache baked into an earlier layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential file zsh git sudo ruby curl vim neovim language-pack-en \
    && rm -rf /var/lib/apt/lists/*

# Create a test user
RUN useradd -ms /bin/bash user && \
        echo "user ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/user && \
        chmod 0440 /etc/sudoers.d/user

USER user:user

WORKDIR /home/user
RUN touch .bash_profile

RUN mkdir -p dotfiles
COPY . dotfiles
CMD ["/bin/bash"]
