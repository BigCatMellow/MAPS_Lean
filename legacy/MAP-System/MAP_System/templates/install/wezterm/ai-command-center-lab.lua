local wezterm = require("wezterm")
local act = wezterm.action

local project_dir = os.getenv("PROJECT_DIR") or "__PROJECT_DIR__"
local local_bin = "__LOCAL_BIN__"

local palette = {
  chrome = "#080b12",
  surface = "#111621",
  surface_hover = "#202838",
  foreground = "#d8dee9",
  muted = "#718096",
  codex = "#5ee6a8",
  claude = "#f3a66a",
  pi = "#bd93f9",
  librarian = "#62d6e8",
  monitor = "#ff6b81",
  shell = "#8fa1b8",
}

local function title_case(value)
  return (value:gsub("^%l", string.upper))
end

local tool_labels = {
  codex = "Codex",
  claude = "Claude",
  pi = "Pi",
}

local function agent_tab_title(title)
  local tool = title:match("%[([%w_-]+)%]%s*$")
  if not tool or not tool_labels[tool] then
    return nil
  end
  local raw_name = title
    :gsub("^%s*◉%s*", "")
    :gsub("%s*%[[^]]+%]%s*$", "")
  local name = raw_name:match("([^-]+)$") or raw_name
  return string.format(
    "%s-%s",
    title_case(name),
    tool_labels[tool]
  )
end

local function tab_style(title)
  local name = title:lower()
  if name:find("codex", 1, true) then
    return palette.codex
  elseif name:find("claude", 1, true) then
    return palette.claude
  elseif name:find("pi ", 1, true) or name == "pi" or name:find("pi lab", 1, true) then
    return palette.pi
  elseif name:find("librarian", 1, true) then
    return palette.librarian
  elseif name:find("monitor", 1, true) then
    return palette.monitor
  end
  return palette.shell
end

wezterm.on("format-tab-title", function(tab, _, _, _, hover)
  local title = tab.tab_title
  local pane_title = tab.active_pane.title
  if pane_title and pane_title:match("%[[%w_-]+%]%s*$") then
    title = pane_title
  elseif not title or title == "" then
    title = tab.active_pane.title
  end

  local label = agent_tab_title(title or "") or title or "Shell"
  local accent = tab_style(title or "")
  local background = tab.is_active and accent or (hover and palette.surface_hover or palette.surface)
  local foreground = tab.is_active and palette.chrome or accent

  return {
    { Background = { Color = palette.chrome } },
    { Foreground = { Color = background } },
    { Text = "" },
    { Background = { Color = background } },
    { Foreground = { Color = foreground } },
    { Attribute = { Intensity = "Bold" } },
    { Text = " " .. label .. " " },
    { Background = { Color = palette.chrome } },
    { Foreground = { Color = background } },
    { Text = "" },
  }
end)

wezterm.on("update-right-status", function(window)
  local status = wezterm.format({
    { Background = { Color = palette.chrome } },
    { Foreground = { Color = palette.muted } },
    { Text = "  " .. window:active_workspace() .. "  " },
    { Foreground = { Color = palette.codex } },
    { Text = "● " },
    { Foreground = { Color = palette.foreground } },
    { Text = wezterm.strftime("%a %b %d  %H:%M") .. "  " },
  })
  window:set_right_status(status)
end)

local function tab(window, title, argv)
  local new_tab, _, _ = window:spawn_tab({
    cwd = project_dir,
    args = argv,
  })
  new_tab:set_title(title)
end

-- TASK-302: the operator requires a fixed, visible startup roster. Each agent
-- starts through its instruction-bearing launcher; extra task-scoped helpers
-- remain on demand. Visibility is not authority: bigboss designates at most
-- one run coordinator from the eligible Codex/Claude core agents; task owners
-- and independent reviewers remain conflict-separated, while Pi and Librarian
-- remain bounded support.
wezterm.on("gui-startup", function(cmd)
  local _, pane, window = wezterm.mux.spawn_window({
    workspace = "ai-command-center-lab",
    cwd = project_dir,
    args = { local_bin .. "/ai-command-center-lab-shell" },
  })
  tab(window, "Codex Lab", { local_bin .. "/ai-command-center-lab-codex" })
  tab(window, "Claude Lab", { local_bin .. "/ai-command-center-lab-claude" })
  tab(window, "Pi Lab", { local_bin .. "/ai-command-center-lab-pi" })
  tab(window, "Librarian", { local_bin .. "/ai-command-center-lab-librarian" })
  tab(window, "New Agent", { local_bin .. "/ai-command-center-new-agent" })
  tab(window, "Monitor", { local_bin .. "/ai-command-center-monitor" })
end)

return {
  automatically_reload_config = true,
  window_close_confirmation = "NeverPrompt",
  enable_tab_bar = true,
  hide_tab_bar_if_only_one_tab = false,
  use_fancy_tab_bar = false,
  tab_bar_at_bottom = false,
  show_new_tab_button_in_tab_bar = false,
  show_tab_index_in_tab_bar = false,
  switch_to_last_active_tab_when_closing_tab = true,
  tab_max_width = 20,
  status_update_interval = 1000,
  font = wezterm.font_with_fallback({
    { family = "JetBrains Mono", weight = "Regular" },
    "Symbols Nerd Font Mono",
    "Ubuntu Mono",
  }),
  font_size = 13.0,
  line_height = 1.0,
  cell_width = 1.0,
  harfbuzz_features = { "calt=0", "clig=0", "liga=0" },
  window_padding = {
    left = 12,
    right = 12,
    top = 10,
    bottom = 8,
  },
  window_background_opacity = 1.0,
  text_background_opacity = 1.0,
  default_cursor_style = "BlinkingBar",
  cursor_blink_rate = 650,
  audible_bell = "Disabled",
  scrollback_lines = 15000,
  adjust_window_size_when_changing_font_size = false,
  bold_brightens_ansi_colors = true,
  colors = {
    foreground = palette.foreground,
    background = "#0d111a",
    cursor_bg = palette.claude,
    cursor_fg = palette.chrome,
    cursor_border = palette.claude,
    selection_fg = "#f7f9fc",
    selection_bg = "#34445c",
    scrollbar_thumb = "#2a3447",
    split = "#2a3447",
    ansi = {
      "#151a24", "#ff6b81", "#5ee6a8", "#f5c26b",
      "#72a7ff", "#bd93f9", "#62d6e8", "#c8d0dc",
    },
    brights = {
      "#68758a", "#ff8fa3", "#80f0be", "#ffda8a",
      "#94bdff", "#d0adff", "#8ae5f1", "#f7f9fc",
    },
    tab_bar = {
      background = palette.chrome,
      active_tab = {
        bg_color = palette.surface,
        fg_color = palette.foreground,
      },
      inactive_tab = {
        bg_color = palette.chrome,
        fg_color = palette.muted,
      },
      inactive_tab_hover = {
        bg_color = palette.surface_hover,
        fg_color = palette.foreground,
      },
      new_tab = {
        bg_color = palette.chrome,
        fg_color = palette.muted,
      },
      new_tab_hover = {
        bg_color = palette.surface_hover,
        fg_color = palette.foreground,
      },
    },
  },
  keys = {
    { key = "1", mods = "CTRL", action = act.ActivateTab(0) },
    { key = "2", mods = "CTRL", action = act.ActivateTab(1) },
    { key = "3", mods = "CTRL", action = act.ActivateTab(2) },
    { key = "4", mods = "CTRL", action = act.ActivateTab(3) },
    { key = "5", mods = "CTRL", action = act.ActivateTab(4) },
    { key = "6", mods = "CTRL", action = act.ActivateTab(5) },
    {
      key = "n",
      mods = "CTRL|SHIFT",
      action = act.SpawnCommandInNewTab({
        cwd = project_dir,
        args = { local_bin .. "/ai-command-center-new-agent" },
      }),
    },
  },
}
