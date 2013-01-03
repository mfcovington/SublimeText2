import sublime, sublime_plugin

class BaseSurroundCommand(sublime_plugin.TextCommand):
  """
  class BaseSurroundCommand(sublime_plugin.TextCommand)
  |
  | An abstract class representing shared behavior for all
  | Surround commands.
  |
  | Static values:
  |
  | MATCHING_CHARS
  | 
  | A dictionary mapping special case surround shortcuts into
  | open, close pairs.  E.g. both open and close parentheses 
  | map to the pair (, ) to make surrounding with parens easier
  |


  """

  # Provides a shortcut for specifying surrounding characters as
  # open, close pairs of characters.  An additional special case
  # is included for xml tag pairs, handled outside of this dict
  MATCHING_CHARS = {
    '{' : ['{', '}'],
    '}' : ['{', '}'],
    '[' : ['[', ']'],
    ']' : ['[', ']'],
    '(' : ['(', ')'],
    ')' : ['(', ')'],
    '<' : ['<', '>'],
    '>' : ['<', '>'],
    '/*' : ['/*', '*/'], # Block comments
    '#' : ['# ',''], # Python style comments
    '//' : ['// ', ''] # Java style comments
  }

  def get_matching_char_pair(self, text):
    if text in self.MATCHING_CHARS:
      return self.MATCHING_CHARS[text]
    # If the text looks like <...> assume its an xml tag
    # and generate the appropriate closing tag
    if text.startswith('<') and text.endswith('>'):
      if text[1] == '/': # Then text is a closing tag
        return [text[0] + text[2:], text]
      return [text, text[0] + "/" + text[1:]] # Otherwise text is open tag
    return [text, text] # surround it with both

  def get_word_to_surround(self, region):
    if region.empty():
      return self.view.word(region.a)
    return region

  def apply_surround_chars(self):
    selected_regions = self.view.sel()
    for region in selected_regions:
      word = self.get_word_to_surround(region)
      self.replace_around_word(self.replace_chars, self.with_chars, word)

  def run(self, edit):
    raise NotImplementedError('The class "BaseSurroundCommand" is an abstract class and should not be used.')

  def apply_surround_chars(self, surround_chars):
    raise NotImplementedError('The class "BaseSurroundCommand" is an abstract class and should not be used.')

  def after_input(self, text):
    raise NotImplementedError('The class "BaseSurroundCommand" is an abstract class and should not be used.')

class AddSurroundCommand(BaseSurroundCommand):
  def run(self, edit):
    self.view.window().show_input_panel('Surround with [text]:', '', self.after_input, None, None)
  
  def after_input(self, text):
    if text:
      surround_chars = self.get_matching_char_pair(text)
      self.apply_surround_chars(surround_chars)
  
  def insert_around_word(self, word, surround_chars):
    edit_sequence = self.view.begin_edit()
    self.view.insert(edit_sequence, word.begin(), surround_chars[0])
    # After inserting the prefix, the end of the word is shifted by the length of the prefix
    self.view.insert(edit_sequence, word.end() + len(surround_chars[0]), surround_chars[1])
    self.view.end_edit(edit_sequence)

class DeleteSurroundCommand(BaseSurroundCommand):
  def run(self, edit):
    self.view.window().show_input_panel('Delete surrounding [text]:', '', self.after_input, None, None)
  
  def after_input(self, text):
    if text:
      surround_chars = self.get_matching_char_pair(text)
      self.apply_surround_chars(surround_chars)

  def delete_surrounding_regions(self, surround_chars, region):
    region_text = self.view.substr(region)
    prefix = sublime.Region(max(0,region.begin() - len(surround_chars[0])), region.begin())
    suffix = sublime.Region(region.end(), min(self.view.size(),region.end() + len(surround_chars[1])))
    if self.view.substr(prefix) == surround_chars[0] and self.view.substr(suffix) == surround_chars[1]:
      edit_sequence = self.view.begin_edit()
      self.view.replace(edit_sequence, prefix, '')
      # After deleting the prefix, the beginning and end of the suffix are shifted by the lenght of the prefix
      self.view.replace(edit_sequence, sublime.Region(suffix.begin() - len(surround_chars[0]), suffix.end() - len(surround_chars[0])), '')
      self.view.end_edit(edit_sequence)

class ReplaceSurroundCommand(BaseSurroundCommand):

  replace_chars = None
  with_chars = None

  def run(self, edit):
    self.view.window().show_input_panel('Replace surrounding: ', '', self.after_replace_input, None, None)
  
  def after_replace_input(self, text):
    if text:
      self.replace_chars = self.get_matching_char_pair(text)
      self.view.window().show_input_panel('With surrounding: ', '', self.after_with_input, None, None)

  def after_with_input(self, text):
    self.with_chars = self.get_matching_char_pair(text)
    self.apply_surround_chars()

  def insert_around_word(self, word, surround_chars):
    edit_sequence = self.view.begin_edit()
    self.view.insert(edit_sequence, word.begin(), surround_chars[0])
    self.view.insert(edit_sequence, word.end() + len(surround_chars[0]), surround_chars[1])
    self.view.end_edit(edit_sequence)`

  def replace_around_word(self, replace_chars, with_chars, region):
    region_text = self.view.substr(region)
    prefix = sublime.Region(max(0,region.begin() - len(replace_chars[0])), region.begin())
    suffix = sublime.Region(region.end(), min(self.view.size(),region.end() + len(replace_chars[1])))
    if self.view.substr(prefix) == replace_chars[0] and self.view.substr(suffix) == replace_chars[1]:
      edit_sequence = self.view.begin_edit()
      self.view.replace(edit_sequence, prefix, '')
      self.view.replace(edit_sequence, sublime.Region(suffix.begin() - len(replace_chars[0]), suffix.end() - len(replace_chars[0])), '')
      self.view.insert(edit_sequence, region.begin() - len(replace_chars[0]), with_chars[0])
      self.view.insert(edit_sequence, region.end() - len(replace_chars[0]) + len(with_chars[0]), with_chars[1])
      self.view.end_edit(edit_sequence)
