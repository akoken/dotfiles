FROM ubuntu

# Install dependencies
RUN apt-get update
RUN apt-get install -y build-essential file zsh git sudo ruby curl vim neovim language-pack-en

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
