import time

# shortcuts for printing card attrobutes in the format string
ATTR_CODES = {
	'%n': '%{name}',
	'%m': '%{mana_cost}',
	'%c': '%{cmc}',
	'%y': '%{type_line}',
	'%p': '%{power}',
	'%t': '%{toughness}',
	'%l': '%{loyalty}',
	'%o': '%{oracle_text}',
	'%f': '%{flavor_text}',
}


def print_cards(cards, formatting):
	# get lines of text to be printed
	lines = []
	for card in cards:
		card_lines = generate_print_lines(card, formatting)
		if card_lines == None:
			continue
		for card_line in card_lines:
			lines.append(card_line)
	if len(lines) < 1:
		return
			
	# calculate column widths
	num_cols = len(lines[0])
	col_widths = [0] * num_cols
	for row in lines:
		for w in range(num_cols):
			col_widths[w] = max(len(row[w]), col_widths[w])
	
	# print the data
	for column_list in lines:
		print_line = ''
		for i in range(num_cols):
			print_line = print_line + '{: <' + str(col_widths[i]) + '}'
		print_line = print_line.format(*column_list)
		print(print_line)


# each card is printed on one line, defined by the formatting string
def generate_print_lines(card, formatting):
	print_line = formatting
	# first put in a placeholder for %%
	percent_placeholder = '{PERCENT' + str(time.time()) + '}'
	while percent_placeholder in print_line:
		percent_placeholder = '{PERCENT' + str(time.time()) + '}'
	print_line = print_line.replace('%%', percent_placeholder)
	# with literal % characters removed from the formatting string,
	# it is easier to process formatted % characters
	
	# replace %x shortcuts with full %{attr} name
	for attr_code in ATTR_CODES:
		print_line = print_line.replace(attr_code, ATTR_CODES[attr_code])
	
	# get %{attr} values
	while True:
		attr_name = get_next_attr_name(print_line)
		if attr_name == None:
			break
		# nested attributes can be chained together with '.'
		attr_list = attr_name.split('.')
		# all nested attributes can be referenced using '*'
		# this probably means each card gets multiple printed lines
		if '*' in attr_list:
			iterated_list = iterate_attr(card, attr_list, print_line)
			if iterated_list == None:
				return None
			for i in range(len(iterated_list)):
				iterated_list[i] = [w.replace(percent_placeholder, '%') for w in iterated_list[i]]
			return iterated_list
		
		attr_value = parse_attr(card, attr_list)
		if attr_value == None:
			return None
		print_line = print_line.replace('%{' + attr_name + '}', attr_value)
	
	print_line = print_line.split('%|')
	print_line = [w.replace(percent_placeholder, '%') for w in print_line]
	return [print_line]


# card attributes are referenced in the formatting string by %{attr}
def get_next_attr_name(line):
	start_idx = line.find('%{')
	if start_idx == -1 or start_idx == len(line) - 2:
		return None
	end_idx = line.find('}', start_idx)
	if end_idx == -1:
		return None
	attr = line[start_idx + 2 : end_idx]
	return attr


# get an attribute of the card defined in json
# nested values are separated by a dot '.'
def parse_attr(card, attr_list):
	value = card
	prev_attr = ''
	for attr in attr_list:
		# this prints the name of the previous attribute, rather than a value
		if attr == '^':
			value = prev_attr
		else:
			value = get_attr_value(value, attr)
		if value == None:
			return None
		prev_attr = attr
	return str(value)


# generate a print line for each item in the attribute marked with '*'
def iterate_attr(card, attr_list, print_line):
	value = card
	attr_replace = '%{'
	for attr in attr_list:
		if attr == '*':
			break
		# construct a string of the nested attributes up until the '*'
		attr_replace += attr + '.'
		value = get_attr_value(value, attr)
		if value == None:
			return None

	results = []
	# iterate differently based on dicts, lists, strings, etc
	if type(value) is dict:
		items = value.keys()
	else:
		items = range(len(value))
	
	for item in items:
		# create a new print line for each element in the itterated attribute
		# each element's name replaces the '*' on that line
		item_line = print_line.replace(attr_replace + '*', attr_replace + str(item))
		# after the replace, run each new line through the process again
		next_result = generate_print_lines(card, item_line)
		if next_result == None:
			continue
		results = results + next_result
	return results


# get the value of an attribute from json data
def get_attr_value(data, attr):
	if type(data) is dict:
		return data.get(attr)
	if attr.isdigit():
		return data[int(attr)]
	return None