return {
  -- { ---- colorscheme.
  --   'sainnhe/gruvbox-material',
  --   lazy = false, -- make sure we load this during startup if it is your main colorscheme
  --   priority = 1000, -- make sure to load this before all the other start plugins
  --   config = function()
  --     vim.cmd [[
  --           " https://github.com/sainnhe/gruvbox-material/blob/master/doc/gruvbox-material.txt
  --           " Important!!
  --           " For dark version.
  --           set background=dark
  --           " Set contrast.
  --           " This configuration option should be placed before `colorscheme gruvbox-material`.
  --           " Available values: 'hard', 'medium'(default), 'soft'
  --           let g:gruvbox_material_background = 'hard'
  --           " For better performance
  --           let g:gruvbox_material_better_performance = 1
  -- 	let g:gruvbox_material_enable_italic = 1
  --
  --           let g:gruvbox_material_diagnostic_text_highlight = 1
  --           " let g:gruvbox_material_diagnostic_line_highlight = 1
  --           let g:gruvbox_material_diagnostic_virtual_text = "colored"
  --           let g:gruvbox_material_sign_column_background = 'none'
  --           let g:gruvbox_material_transparent_background = 2
  --
  --           colorscheme gruvbox-material
  --           ]]
  --   end,
  -- },
  -- {
  --   'catppuccin/nvim',
  --   priority = 1000,
  --   name = 'catppuccin',
  --   config = function()
  --     require('catppuccin').setup {
  --       flavour = 'mocha', -- latte, frappe, macchiato, mocha
  --       background = { -- :h background
  --         light = 'latte',
  --         dark = 'mocha',
  --       },
  --       transparent_background = true, -- disables setting the background color.
  --       show_end_of_buffer = false, -- shows the '~' characters after the end of buffers
  --       term_colors = false, -- sets terminal colors (e.g. `g:terminal_color_0`)
  --       dim_inactive = {
  --         enabled = false, -- dims the background color of inactive window
  --         shade = 'dark',
  --         percentage = 0.15, -- percentage of the shade to apply to the inactive window
  --       },
  --       no_italic = false, -- Force no italic
  --       no_bold = false, -- Force no bold
  --       no_underline = false, -- Force no underline
  --       styles = { -- Handles the styles of general hi groups (see `:h highlight-args`):
  --         comments = { 'italic' }, -- Change the style of comments
  --         conditionals = { 'italic' },
  --         loops = {},
  --         functions = {},
  --         keywords = {},
  --         strings = {},
  --         variables = {},
  --         numbers = {},
  --         booleans = {},
  --         properties = {},
  --         types = {},
  --         operators = {},
  --         -- miscs = {}, -- Uncomment to turn off hard-coded styles
  --       },
  --       color_overrides = {},
  --       custom_highlights = {},
  --       integrations = {
  --         cmp = true,
  --         gitsigns = true,
  --         nvimtree = true,
  --         treesitter = true,
  --         notify = false,
  --         telescope = {
  --           enabled = true,
  --         },
  --         mini = {
  --           enabled = true,
  --           indentscope_color = '',
  --         },
  --         -- For more plugins integrations please scroll down (https://github.com/catppuccin/nvim#integrations)
  --       },
  --     }
  --
  --     -- setup must be called before loading
  --     -- vim.cmd.colorscheme 'catppuccin'
  --   end,
  -- },
  -- {
  --   'lunarvim/synthwave84.nvim',
  --   priority = 1000,
  --   name = 'synthwave84',
  --   config = function()
  --     require('synthwave84').setup {
  --       glow = {
  --         error_msg = true,
  --         type2 = true,
  --         func = true,
  --         keyword = true,
  --         operator = false,
  --         buffer_current_target = true,
  --         buffer_visible_target = true,
  --         buffer_inactive_target = true,
  --       },
  --     }
  --
  --     -- setup must be called before loading
  --     --vim.cmd.colorscheme 'synthwave84'
  --   end,
  -- },
  {
    'maxmx03/fluoromachine.nvim',
    config = function()
      local fm = require 'fluoromachine'

      fm.setup {
        glow = false,
        theme = 'delta',
        --theme = 'retrowave',
        transparent = 'full',
      }

      vim.cmd.colorscheme 'fluoromachine'
    end,
  },
}
