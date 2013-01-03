import sublime, sublime_plugin
import re

indent_matcher = re.compile("^[ ]*")
def current_indent(s):
	return len(indent_matcher.match(s).group(0))

operator_split_matcher = re.compile("[ \[\]\(\)\{\}]")
def get_operator(line_str, idx):
	operator_str = line_str[idx + 1:]
	return operator_split_matcher.split(operator_str)[0]

def bracket_indent(idx):      return idx + 1
def two_space_indent(idx):    return idx + 2
def operator_indent(op, idx): return idx + len(op) + 2

whitespace_matcher = re.compile("\s*$")
def parentheses_indent(line_str, idx, options):
	op = get_operator(line_str, idx)
	
	if op == "": return bracket_indent(idx)
	elif whitespace_matcher.match(line_str[idx + len(op) + 1:]):
		return two_space_indent(idx)

	is_match = options['regex'].match(op)
	if options["default_indent"] == "two_space":
		if is_match: return operator_indent(op, idx)
		else:        return two_space_indent(idx)
	else:
		if is_match: return two_space_indent(idx)
		else:        return operator_indent(op, idx)
	return idx + 2

def update_counts(counts, char):
	(pa, br, cbr) = counts
	if char == '(': pa += 1
	elif char == ')': pa -= 1
	elif char == '[': br += 1
	elif char == ']': br -= 1
	elif char == '{': cbr += 1
	elif char == '}': cbr -= 1
	return (pa, br, cbr)

comment_matcher = re.compile(";[^\"]*$")
char_matcher = re.compile("\\\\[\(\)\[\]\{\}]")
def indent(view, idx, options):
	lines = reversed(view.split_by_newlines(sublime.Region(0, idx)))
	pa, br, cbr = 0, 0, 0
	is_outside_str = True
	for line in lines:
		line_str = char_matcher.sub("",
		             comment_matcher.sub("", 
		               view.substr(line)))
		for idx in range(len(line_str) - 1, -1, -1):
			c = line_str[idx]
			if c == "\"": is_outside_str = not is_outside_str
			if is_outside_str:
				(pa, br, cbr) = update_counts((pa, br, cbr), c)
				if br > 0 or cbr > 0: return bracket_indent(idx)
				elif pa > 0:
					if idx > 0 and line_str[idx - 1] == "'":
						return bracket_indent(idx)
					else:
						return parentheses_indent(line_str, idx, options)
		if pa == 0 and br == 0 and cbr == 0:
			return current_indent(line_str)
	return 0

def get_indent_str(view, idx, options):
	return " " * indent(view, idx, options)