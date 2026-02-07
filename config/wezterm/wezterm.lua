--
-- ██╗    ██╗███████╗███████╗████████╗███████╗██████╗ ███╗   ███╗
-- ██║    ██║██╔════╝╚══███╔╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
-- ██║ █╗ ██║█████╗    ███╔╝    ██║   █████╗  ██████╔╝██╔████╔██║
-- ██║███╗██║██╔══╝   ███╔╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
-- ╚███╔███╔╝███████╗███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
--  ╚══╝╚══╝ ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
-- A GPU-accelerated cross-platform terminal emulator
-- https://wezfurlong.org/wezterm/

local dark_opacity = 0.9
local light_opacity = 0.9

local wallpapers_glob = "/Users/akoken/Documents/Wallpapers/active/**"

local b = require("utils/background")
local cs = require("utils/color_scheme")
local w = require("utils/wallpaper")

local wezterm = require("wezterm")

local config = {
	background = {
		w.get_wallpaper(wallpapers_glob),
		b.get_background(dark_opacity, light_opacity),
	},

	--line_height = 1.1,
	font_size = 18,
	font = wezterm.font_with_fallback({
		"MonoLisa",
		--"PragmataPro",
		"Cartograph CF",
		"Liga SFMono Nerd Font",
	}),

	color_scheme = cs.get_color_scheme(),

	window_padding = {
		left = 20,
		right = 20,
		top = 20,
		bottom = 20,
	},

	set_environment_variables = {
		BAT_THEME = cs.get_color_scheme(),
		LC_ALL = "en_US.UTF-8",
	},

	-- general options
	front_end = "WebGpu",
	adjust_window_size_when_changing_font_size = false,
	debug_key_events = false,
	enable_tab_bar = false,
	native_macos_fullscreen_mode = false,
	window_close_confirmation = "NeverPrompt",
	window_decorations = "RESIZE",
	default_cursor_style = "SteadyBar",
	max_fps = 120,
	animation_fps = 120,

	-- keys
	keys = {
		-- Sends ESC + b and ESC + f sequence, which is used
		-- for telling your shell to jump back/forward.
		{
			-- When the left arrow is pressed
			key = "LeftArrow",
			-- With the "Option" key modifier held down
			mods = "OPT",
			-- Perform this action, in this case - sending ESC + B
			-- to the terminal
			action = wezterm.action.SendString("\x1bb"),
		},
		{
			key = "RightArrow",
			mods = "OPT",
			action = wezterm.action.SendString("\x1bf"),
		},
		{
			key = "A",
			mods = "CTRL|SHIFT",
			action = wezterm.action.QuickSelect,
		},
	},
}

return config
