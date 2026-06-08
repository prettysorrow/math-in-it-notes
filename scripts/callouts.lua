function BlockQuote(block)
  local first = block.content[1]
  if not (first and first.t == 'Para') then return nil end
  local inlines = first.content
  if #inlines == 0 then return nil end
  local first_str = inlines[1]
  if first_str.t ~= 'Str' then return nil end

  local typ = first_str.text:match('^%[!(%w+)%]$')
  if not typ then return nil end

  table.remove(inlines, 1)
  if #inlines > 0 and inlines[1].t == 'Space' then
    table.remove(inlines, 1)
  end

  -- split first Para at first SoftBreak: title / body
  local title_il, body_il = {}, {}
  local found = false
  for _, il in ipairs(inlines) do
    if il.t == 'SoftBreak' and not found then
      found = true
    elseif not found then
      table.insert(title_il, il)
    else
      table.insert(body_il, il)
    end
  end

  local new_blocks = {}
  if #title_il > 0 then
    table.insert(new_blocks, pandoc.Para(title_il))
  end
  if #body_il > 0 then
    table.insert(new_blocks, pandoc.Para(body_il))
  end
  for i = 2, #block.content do
    table.insert(new_blocks, block.content[i])
  end
  block.content = new_blocks

  local doc = pandoc.Pandoc(block.content, {})
  local body = pandoc.write(doc, 'latex')
  body = body:gsub('~', ' ')

  return pandoc.RawBlock('latex',
    '\\begin{callout}{' .. typ .. '}\n' ..
    body ..
    '\\end{callout}\n'
  )
end
