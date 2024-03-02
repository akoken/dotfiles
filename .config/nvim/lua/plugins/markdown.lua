return {
  {
    "iamcco/markdown-preview.nvim",
    event = "VeryLazy",
    cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
    ft = { "markdown", "md" },
    build = function()
      vim.fn["mkdp#util#install"]()
    end,
  },
  {
    "ellisonleao/glow.nvim",
    cmd = "Glow",
    ft = { "markdown", "md" },
    opts = {
      style = "dark",
    },
  },
}
