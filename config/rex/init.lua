-- Rex configuration, migrated from tmux, Herdr, Ghostty and WezTerm.

-- Pass the prefix through to programs that use it themselves.
rex.bind("ctrl+a>ctrl+a", "pane.send_key", { key = "ctrl+a" })

-- tmux (~/.config/tmux/tmux.reset.conf)
rex.bind("ctrl+a>b", "client.tab.new")
rex.bind("ctrl+a>shift+h", "client.tab.previous")
rex.bind("ctrl+a>shift+l", "client.tab.next")
rex.bind("ctrl+a>r", "client.tab.rename")
rex.bind("ctrl+a>shift+r", "client.config.reload")
rex.bind("ctrl+a>z", "pane.zoom")
rex.bind("ctrl+a>shift+\\", "pane.split", { direction = "down" })
rex.bind("ctrl+a>s", "pane.split", { direction = "down" })
rex.bind("ctrl+a>v", "pane.split", { direction = "right" })
rex.bind("ctrl+a>shift+'", "session.switch")
rex.bind("ctrl+a>h", "pane.focus", { direction = "left" })
rex.bind("ctrl+a>j", "pane.focus", { direction = "down" })
rex.bind("ctrl+a>k", "pane.focus", { direction = "up" })
rex.bind("ctrl+a>l", "pane.focus", { direction = "right" })
rex.bind("ctrl+a>,", "pane.resize", { amount = 20, direction = "left" })
rex.bind("ctrl+a>.", "pane.resize", { amount = 20, direction = "right" })
rex.bind("ctrl+a>-", "pane.resize", { amount = 7, direction = "down" })
rex.bind("ctrl+a>=", "pane.resize", { amount = 7, direction = "up" })
rex.bind("ctrl+a>c", "pane.close")
rex.bind("ctrl+a>x", "pane.move", { direction = "down" })
rex.bind("ctrl+a>shift+s", "session.switch")

-- tmux repeatable bindings (bind -r), as a key mode
rex.mode("repeat", { exclusive = true })
rex.bind("ctrl+a>ctrl+r", "client.mode.enter", { name = "repeat" })
rex.bind("repeat/enter", "client.mode.exit")
rex.bind("repeat/escape", "client.mode.exit")
rex.bind("repeat/,", "pane.resize", { amount = 20, direction = "left" })
rex.bind("repeat/.", "pane.resize", { amount = 20, direction = "right" })
rex.bind("repeat/-", "pane.resize", { amount = 7, direction = "down" })
rex.bind("repeat/=", "pane.resize", { amount = 7, direction = "up" })

-- Herdr (~/.config/herdr/config.toml); shared keys keep tmux's binding
rex.bind("ctrl+a>o", "session.switch")
rex.bind("ctrl+a>w", "session.new")
rex.bind("ctrl+a>shift+w", "session.rename")
rex.bind("ctrl+a>g", "session.switch")
rex.bind("ctrl+a>m", "client.sidebar.toggle")
