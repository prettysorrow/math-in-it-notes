local function is_word_char(char)
  local b1 = char:byte(1)
  if not b1 then return false end
  if b1 < 128 then
    return char:match('^[%w%s%-]$') ~= nil
  end
  if b1 >= 0xD0 and b1 <= 0xD4 then return true end
  if b1 >= 0xC3 and b1 <= 0xC5 then return true end
  return false
end

function Header(el)
  local text = pandoc.utils.stringify(el.content):lower()
  local chars = {}
  for char in text:gmatch(utf8.charpattern) do
    if is_word_char(char) then
      table.insert(chars, char)
    end
  end
  local slug = table.concat(chars)
  slug = slug:gsub('%s+', '-')
  slug = slug:gsub('%-+', '-')
  slug = slug:gsub('^%-*(.-)%-*$', '%1')
  if slug ~= '' then
    el.identifier = slug
  end
  return el
end
