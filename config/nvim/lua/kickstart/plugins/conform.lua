return {
  { -- Autoformat
    'stevearc/conform.nvim',
    opts = {
      notify_on_error = false,
      format_on_save = function(bufnr)
        -- Disable "format_on_save lsp_fallback" for languages that don't
        -- have a well standardized coding style. You can add additional
        -- languages here or re-enable it for the disabled ones.
        local disable_filetypes = { c = true, cpp = true }
        return {
          timeout_ms = 500,
          lsp_fallback = not disable_filetypes[vim.bo[bufnr].filetype],
        }
      end,
      formatters_by_ft = {
        css = { 'prettierd' },
        html = { 'prettierd' },
        javascript = { 'prettierd' },
        json = { 'prettierd' },
        jsonc = { 'prettierd' },
        lua = { 'stylua' },
        sh = { 'shfmt', 'shellharden' },
        bash = { 'shfmt', 'shellharden' },
        markdown = { 'cbfmt', 'prettierd', 'markdownlint' },
        go = { 'goimports', 'gofumpt' }, -- gofmt, gomodifytags
        templ = {
          'gofumpt',
          'templ',
          'injected',
        },
        -- Conform can also run multiple formatters sequentially
        -- python = { "isort", "black" },
        --
        -- You can use a sub-list to tell conform to run *until* a formatter
        -- is found.
        -- javascript = { { "prettierd", "prettier" } },
      },
    },
  },
}
-- vim: ts=2 sts=2 sw=2 et
