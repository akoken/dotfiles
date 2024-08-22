return {
  {
    'maxmx03/fluoromachine.nvim',
    config = function()
      local fm = require 'fluoromachine'

      fm.setup {
        glow = false,
        theme = 'delta',
        transparent = 'full',
      }

      vim.cmd.colorscheme 'fluoromachine'
    end,
  },
}
