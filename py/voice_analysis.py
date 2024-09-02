import music21 as m21
import os
import sys
import statistics
import numpy as np
import pandas as pd
import seaborn as sns
#sns.set_style('darkgrid')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import math
from fractions import Fraction
import string

# Call this script from the folder containing it.

# Get unique list items (see https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python)
#unique_items = set(a_list)
#unique_items = list(unique_items)
# Sort list (in-place) by property of list items (see https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects)
#a_list.sort(key=lambda x: x.a_property)

path = os.getcwd()
pieces_with_illegal_part_names = []


def get_vocal_parts(parts, piece):
	"""Gets only the vocal parts of the given parts.
       NB: It is assumed that the parts are iterated over in the same sequence as they 
		   appear in get_vocal_parts()
	Args: 
		parts (music21.stream.iterator.StreamIterator): A list of music21.stream.Part objects.

	Returns:
		list: The vocal parts (a list of music21.stream.Part objects). 
	"""

	for count, part in enumerate(parts):
#		# NB part.partName must be used here, as part.id gives a different name in case of
#		# a divided part (e.g., part.partName is 'Mean', part.id is 'P1-Staff1' or 'P1-Staff2') 
#		if 'viol' in part.partName.lower():
#			parts = parts[:count]
#			break

		name = part.getInstrument().partName
		name_lower = name.lower()
		alt_viol_names = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII','VIII', 
					      'Ib', 'IIb', 'IIIb', 'IVb', 'Vb', 'VIb', 'VIIb','VIIIb'] 
		
		if 'viol' in name_lower or name in alt_viol_names:
			parts = parts[:count]
			if name in alt_viol_names:
				if not piece in pieces_with_illegal_part_names:
					pieces_with_illegal_part_names.append(piece)  
			break

	return parts


def get_min_max_pitch(parts):
	"""Gets the minimum and maximum pitch encountered in the given parts.

	Args: 
		parts (list): A list of music21.stream.Part objects.

	Returns:
		list: A list containing min_pitch and max_pitch, both tuples consisting of an m21.pitch.Pitch 
		      element and its MIDI number.
	"""

	min_pitch = 1000
	max_pitch = 0
	for p in parts:
		ambitus = m21.analysis.discrete.Ambitus().getPitchSpan(p)
		min_p = ambitus[0].midi
		if min_p < min_pitch:
			min_pitch = min_p
		max_p = ambitus[1].midi
		if max_p > max_pitch:
			max_pitch = max_p 

	min_pitch = (m21.pitch.Pitch(min_pitch), min_pitch)
	max_pitch = (m21.pitch.Pitch(max_pitch), max_pitch)
	return [min_pitch, max_pitch]


def add_counts_above_bars(ax, count_is_int):	
	# Add counts above bars (see https://datascience.stackexchange.com/questions/48035/how-to-show-percentage-text-next-to-the-horizontal-bars-in-matplotlib),
	# centered (see https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html)
	for p in ax.patches:
		#	x = p.get_x() + p.get_width() + 0.02
		#	y = p.get_y() + p.get_height()/2
		x = p.get_x() + p.get_width()/2 #+ 0.02
		y = p.get_y() + p.get_height() + 0.5 #/2
		#	ax.annotate(percentage, (x, y))
		num = p.get_height()
		# Convert all non-NaN values to int (NaN is given for 0 values)
		if not math.isnan(num):
			if count_is_int:
				num = int(num)
			else:
				# Round for things such as 2.000000001
				ndigits = 8
				num = round(num, ndigits)
				# Separate left and right of floating point
				left_and_right = math.modf(num)
				left = left_and_right[1] 
				right = left_and_right[0]
				# Set right to multiple of 1/12 and recombine
				possible_rights_ternary = [Fraction(i, 12) for i in range(1, 12)]
				possible_rights_binary = [Fraction(i, 16) for i in range(1, 16)]
				possible_rights = possible_rights_ternary
				for f in possible_rights_binary:
					if f not in possible_rights:
						possible_rights.append(f)
				possible_rights.sort()
				for f in possible_rights:
					if math.isclose(right, f, rel_tol=1e-6): # NB: rel_tol should be smaller than ndigits 
						num = Fraction(left) + f # num is Fraction
						#if num_as_float.is_integer()
						break
				# int fractions (those with a 1 in the denominator) are turned to floats; so 
				# num is either a fraction or a float 
				if isinstance(num, float):
					if num.is_integer():
						num = int(num)
				else:
					# E.g. 13/2 = 12/2 + 1/2
					numer = num.numerator
					denom = num.denominator
					rest = numer%denom 
					whole = (numer - rest) / denom
					frac = str(rest) + '/' + str(denom)
					if whole == 0:
						num = frac 
					else:
						num = str(int(whole)) + ' ' + frac			
		as_string = str(num)
		if num != 0:
#			ax.annotate(num, (x, y), ha='center')
			ax.annotate(as_string, (x, y), ha='center', rotation=90)
		
	return ax


def plot(data, bins_list, x_tick_labels, suptitle, title, part_name, max_dur_piece, add_counts, save_path, save, type):

	sns.set_style('darkgrid')
	plt.figure(figsize=(12,8))

	if type == 'count':
		# Use order=<list> to include also bins with 0 values 
		# (see https://stackoverflow.com/questions/45352766/python-seaborn-plotting-frequencies-with-zero-values)
		ax = sns.countplot(data=data, x='pitch', order=bins_list)
		count_is_int = True
		max_y = 55 # TODO determine from data
		title_suffix = ', total count per pitch'
		file_name_suffix = '-pitch_count'  
	elif type == 'bar':
		ax = sns.barplot(data=data, x=bins_list, y='duration')
		count_is_int = False
#		max_y = max(data['duration'])
		max_y = max_dur_piece
		plt.ylabel('duration')
		title_suffix = ', total duration (in semibreves) per pitch' 
		file_name_suffix = '-pitch_dur'

	if add_counts:
		ax = add_counts_above_bars(ax, count_is_int)

	# X-axis
	ax.set_xticklabels(x_tick_labels)
	plt.xlabel('pitch')
	
	# Y-axis
	y_step_size = 2
	# Set max_y to closest multiple of y_step_size + y_step_size 
	for i in range(0, 10):
		if (math.ceil(max_y) + i) % y_step_size == 0:
			max_y = math.ceil(max_y) + i
			break
	max_y += y_step_size
#	max_y = 94 # determined from the data: 'Nicholson When Jesus sat CADB.musicxml' has the max value of 92.75
	plt.ylim(0, max_y)
	# Ensure ints on y-axis
	plt.yticks(range(0, max_y, y_step_size))

	# Titles	
	plt.suptitle(suptitle)
	plt.title(title + title_suffix)
	
	# Plot
	plt.plot()
	if not save:
		plt.show()
	else:
#		print(save_path)
#		plt.savefig(save_path + part_name.lower().replace(' ', '_') + file_name_suffix + '.png')
		plt.savefig(os.path.join(save_path, part_name.lower().replace(' ', '_') + file_name_suffix + '.png'))
	plt.clf()


def main():
	add_counts = False
	plot_averages = False
	save = True
#	system = 'win'
#	system = 'mac'
#	sep = '/' if system == 'mac' else '\\'
	folder = 'final_batch'
#	folder = 'gibbons-10_pcs-avg'
#	folder = 'three_extra_pieces'
	xml_path = os.path.join(path, folder)
	print('path    :', path)
	print('xml_path:', xml_path)
	print()

	pieces = [p for p in os.listdir(xml_path) if (p.endswith('.xml') or p.endswith('.musicxml'))]
	pieces.sort()

	print('pieces in xml_path:')
	for item in pieces:
		print(item)
	print()

	# Get scores and vocal parts for all pieces
	scores_all_pieces = []
	parts_all_pieces = []
	total_parts = 0
	for piece in pieces:
		print(piece)
		xml_path_piece = os.path.join(xml_path, piece)
		# score is a stream.Score object
		score = m21.converter.parse(xml_path_piece)
		scores_all_pieces.append(score)
		
		# parts is a stream.iterator.StreamIterator object containing stream.Part objects,
		# (accessible by index or name), containing stream.Measure objects (accessible by
		# index)   
		parts = score.parts
		# Only include vocal parts
		parts = get_vocal_parts(parts, piece)
		total_parts += len(parts)
		parts_all_pieces.append(parts)

	# Get lowest and highest pitch of all pieces
	# Flatten parts_all_pieces
	flattened = [item for sublist in parts_all_pieces for item in sublist]
	min_pitch, max_pitch = get_min_max_pitch(flattened)
	print('total number of pieces:', len(pieces))
	print('total number of parts :', total_parts) 
	print('total ambitus         :', str(min_pitch[1]) + ' (' + min_pitch[0].nameWithOctave + ')' + '-' + 
									 str(max_pitch[1]) + ' (' + max_pitch[0].nameWithOctave + ')')
	print()

#	total number of pieces: 124
#	total number of parts : 676
#	total ambitus         : 36 (C2)-81 (A5)

	# Get range as MIDI numbers and as pitch objects
	pitch_range_midi = np.arange(min_pitch[1], max_pitch[1]+1, dtype=int)
	pitch_range_note = np.asarray([m21.pitch.Pitch(midi_p) for midi_p in pitch_range_midi])

	# Add note before/after if first/last note is a sharp or a flat
	# See http://web.mit.edu/music21/doc/moduleReference/modulePitch.html
	# and http://web.mit.edu/music21/doc/moduleReference/modulePitch.html#accidental
	first_note = pitch_range_note[0]
	last_note = pitch_range_note[-1]
	# NB: A non-altered note n can have no accidental but also an accidental with name 'natural'
	if first_note.accidental is not None and first_note.accidental.name != 'natural': 
		first_midi = pitch_range_midi[0] - 1
		pitch_range_midi = np.insert(pitch_range_midi, 0, first_midi)
		pitch_range_note = np.insert(pitch_range_note, 0, m21.pitch.Pitch(first_midi))
	if last_note.accidental is not None and last_note.accidental.name != 'natural':
		last_midi = pitch_range_midi[-1] + 1
		pitch_range_midi = np.append(pitch_range_midi, last_midi)
		pitch_range_note = np.append(pitch_range_note, m21.pitch.Pitch(last_midi))

	# Remove all non-diatonic (sharps and flats) x_tick labels
	allowed_pitches = [p.midi % 12 for p in m21.scale.MajorScale('c').getPitches('c4', 'b4')]
	diatonic_tick_labels = [p.nameWithOctave if p.midi % 12 in allowed_pitches else '' for p in pitch_range_note]
#	diatonic_tick_labels = [p if p.midi % 12 in allowed_pitches else '' for p in pitch_range_note]

#	print(diatonic_tick_labels)
	for i, p in enumerate(diatonic_tick_labels):
		if p == 'G2':
			gamma = '\u0393'.encode('utf-8')
			diatonic_tick_labels[i] = p + '\n|\n(\u0393 ut)'
#			diatonic_tick_labels[i] = p + '\n|\n(G ut)'
		if p == 'C3':
			diatonic_tick_labels[i] = p + '\n|\n(C fa ut)'
		if p == 'C4':
			diatonic_tick_labels[i] = p + '\n|\n(C sol fa ut)'
		if p == 'C5':
			diatonic_tick_labels[i] = p + '\n|\n(C sol fa)'	
#		print(diatonic_tick_labels)
#		print(sys.getdefaultencoding())
#		print('\u00E6')
#		print('\u0393')

	all_meter_strings = []
	all_meters = []
	all_part_names = []
	all_max_dur = []
	max_dur_overall = 0
	piece_with_max_dur = None
	plotting_data_per_part_all_pieces = []
	for count, piece in enumerate(pieces):
#		print('... processing', piece, '...')
		print('piece         :', piece)
		score = scores_all_pieces[count]
		parts = parts_all_pieces[count]
		part_names = [p.id for p in parts]		
#		print('part names:', part_names)

		composer = score.metadata.composer
		if composer is None:
			composer = 'None'
		composer = composer.replace('\n', ' ')
		composer = composer.strip()

		piece_name = score.metadata.title.strip()
		piece_name = piece_name.replace('\n', ' ')
		comp_piece = composer + ' - ' + piece_name

		if composer.startswith('['):
			composer = composer[1:]
		if composer.endswith(']'):
			composer = composer[:-1]

#		for p in parts:
#			if isinstance(p, m21.stream.PartStaff):
#				print(p.getElementsByClass(m21.stream.Measure))

#		# Get range as MIDI numbers and as pitch objects
#		pitch_range_midi = np.arange(min_pitch[1], max_pitch[1]+1, dtype=int)
#		pitch_range_note = np.asarray([m21.pitch.Pitch(midi_p) for midi_p in pitch_range_midi])
#
#		# Add note before/after if first/last note is a sharp or a flat
#		# See http://web.mit.edu/music21/doc/moduleReference/modulePitch.html
#		# and http://web.mit.edu/music21/doc/moduleReference/modulePitch.html#accidental
#		first_note = pitch_range_note[0]
#		last_note = pitch_range_note[-1]
#		# NB: A non-altered note n can have no Accidental but also an accidental with name 'natural'
#		if first_note.accidental is not None and first_note.accidental.name != 'natural': 
#			first_midi = pitch_range_midi[0] - 1
#			pitch_range_midi = np.insert(pitch_range_midi, 0, first_midi)
#			pitch_range_note = np.insert(pitch_range_note, 0, m21.pitch.Pitch(first_midi))
#		if last_note.accidental is not None and last_note.accidental.name != 'natural':
#			last_midi = pitch_range_midi[-1] + 1
#			pitch_range_midi = np.append(pitch_range_midi, last_midi)
#			pitch_range_note = np.append(pitch_range_note, m21.pitch.Pitch(last_midi))
#
#		# Remove all non-diatonic (sharps and flats) x_tick labels
#		allowed_pitches = [p.midi % 12 for p in m21.scale.MajorScale('c').getPitches('c4', 'b4')]
#		diatonic_tick_labels = [p.nameWithOctave if p.midi % 12 in allowed_pitches else '' for p in pitch_range_note]
##		diatonic_tick_labels = [p if p.midi % 12 in allowed_pitches else '' for p in pitch_range_note]
#
##		print(diatonic_tick_labels)
#		for i, p in enumerate(diatonic_tick_labels):
#			if p == 'G2':
#				gamma = '\u0393'.encode('utf-8')
#				diatonic_tick_labels[i] = p + '\n|\n(\u0393 ut)'
#				diatonic_tick_labels[i] = p + '\n|\n(G ut)'
#			if p == 'C3':
#				diatonic_tick_labels[i] = p + '\n|\n(C fa ut)'
#			if p == 'C4':
#				diatonic_tick_labels[i] = p + '\n|\n(C sol fa ut)'
#			if p == 'C5':
#				diatonic_tick_labels[i] = p + '\n|\n(C sol fa)'	
##		print(diatonic_tick_labels)
##		print(sys.getdefaultencoding())
##		print('\u00E6')
##		print('\u0393')

		# Get all meters in the first part (representative for the meters in the complete piece)
		meters_first_part = []
		measures_first = parts[0].getElementsByClass(m21.stream.Measure)
		num_bars_first = len(measures_first)
		for i, measure in enumerate(measures_first, start=1):
			for item in measure:
				if isinstance(item, m21.meter.TimeSignature):
					meters_first_part.append([item, i])
#		print('meters:')
#		for meter in meters_first_part:
#			print(meter[0])

		# Determine the piece length (measured in whole notes)
		len_piece = 0
		ternary_meters = []
		# Single meter		
		if len(meters_first_part) == 1:
			meter_str = meters_first_part[0][0].ratioString
			meter_as_fraction = Fraction(int(meter_str.split('/')[0]), int(meter_str.split('/')[1]))
			numer = meter_str.split('/')[0]
			if numer == '3' or numer == '6' or numer == '9' or numer == '12':
				meter_as_fraction = meter_as_fraction * Fraction(2, 3)
			len_piece = num_bars_first * meter_as_fraction
		# Multiple meters
		else:
			for i, meter in enumerate(meters_first_part):
				meter_str = meter[0].ratioString
				first_bar = meter[1]
				meter_as_fraction = Fraction(int(meter_str.split('/')[0]), int(meter_str.split('/')[1]))
				numer = meter_str.split('/')[0]
				if numer == '3' or numer == '6' or numer == '9' or numer == '12':
					meter_as_fraction = meter_as_fraction * Fraction(2, 3)
					ternary_meters.append(meter_str)

				# Example for piece with 108 bars: bb. 1-55 = 4/2; bb. 56-77 = 6/2; bb. 78-108 = 4/2
				# meters change at 1, 56, 78
				# 56-1 bars in 4/2;  78-56 bars in 6/2; (108+1)-78 bars in 4/2
				# All meters but the last
				if i < len(meters_first_part)-1:
					first_bar_next = meters_first_part[i+1][1]
				# Last meter
				else:
					first_bar_next = num_bars_first + 1
				num_bars_in_meter = first_bar_next - first_bar
				len_piece += num_bars_in_meter * meter_as_fraction	
	
		print('piece length  :', len_piece, '(semibreves)')
		print('main meter    :', meters_first_part[0][0].ratioString)
		print('ternary meters:', ternary_meters)

		

#		if len(ternary_meters) > 0:
#			sdfsdfd

		# For each Part or PartStaff
		clefs_upper_partstaff = []
		key_sigs_upper_partstaff = []
		meters_upper_partstaff = []
		notes_upper_partstaff = []
		notes_upper_partstaff_df = None

		clefs_header = ['sign', 'line', '8va', 'bar']
		key_sigs_header = ['key', 'bar']
		meters_header = ['meter', 'bar']
		notes_header = ['note', 'pitch', 'duration', 'bar', 'meter']
		durs_header = ['note', 'pitch', 'duration']
		rests_header = ['rest', 'duration', 'bar', 'meter']
		max_dur_piece = 0
		plotting_data_per_part = []
		for i, part in enumerate(parts):
#			print('--->', part)

			# part is stream.Part (or, in case of split parts, stream.PartStaff) object, containing 
			# instrument.Instrument, spanner.Slur, and stream.Measure objects
			measures = part.getElementsByClass(m21.stream.Measure)						
			num_bars = len(measures)
			clefs = [] # [clefs_header]
			key_sigs = [] # [key_sigs_header]
			meters = [] # [meters_header]

			if not part.partName in all_part_names:
				all_part_names.append(part.partName)

			# If there is a PartStaff division, the upper item takes the full voice, and the lower item 
			# only the lower notes where it divides
			is_non_divided = part.partName == part.id

			# Remove any unwanted symbols in part name and ID 
			# 'Nicholson When Jesus sat CADB.musicxml' has a part named 'Ten/Bass'
			part.partName = part.partName.replace('/', '-') if '/' in part.partName else part.partName
			part.id = part.id.replace('/', '-') if '/' in part.id else part.id
			# 'Ravenscroft 10 O clap your hands CADB.musicxml' has a part named '? [Altus ed]''
			part.partName = part.partName.replace('?', '') if '?' in part.partName else part.partName
			part.id = part.id.replace('?', '') if '?' in part.id else part.id

#			print(part.partName)
#			print(part.id)

			if not is_non_divided: # should no longer be the case
				print(piece)
				print('PartStaff division')
				print('part.partName:' + '-->' + part.partName + '<--')
				print('part.ID:', part.id)
				exit(0)
			is_upper_partstaff = 'Staff1' in part.id
			is_lower_partstaff = 'Staff2' in part.id
			# Check for exception: upper partstaff with no lower partstaff (e.g., Bassus in _O all true
			# faithful hearts_)
			is_upper_without_lower = False

			if is_upper_partstaff:
				# Check if the next part (if any) is indeed a lower partstaff
				if i < len(parts) - 1 and 'Staff2' not in parts[i+1].id or i == len(parts) - 1:
					is_upper_without_lower = True

			# In case of lower partstaff: adopt clefs, key sigs, and meters from upper partstaff
			if is_lower_partstaff:
				clefs = []
				bar_col = clefs_upper_partstaff[0].index('bar')
				clef_change_bars = [row[bar_col] for row in clefs_upper_partstaff]
				print(clef_change_bars)
				key_sigs = []
				bar_col = key_sigs_upper_partstaff[0].index('bar')
				key_sig_change_bars = [row[bar_col] for row in key_sigs_upper_partstaff]
				print(key_sig_change_bars)
				meters = []
				bar_col = meters_upper_partstaff[0].index('bar')
				meter_change_bars = [row[bar_col] for row in meters_upper_partstaff]
				print(meter_change_bars)

			# 1. Create notes and notes_df, containing information on each note in the part
			notes = []
			rests = []
			max_dur_part = 0
			for j, measure in enumerate(measures, start=1): # start at 1 because element 0 is bar 1
				# If a part is divided into PartStaffs, the lower partstaff does not contain clef, key sig, and 
				# meter items - so clefs, key_sigs, and meters must be built from the upper PartStaff lists (clefs,
				# key sigs and meters should be exactly the same in both PartStaffs)
				# Incrementally build clefs, key sigs and meters by adding the corresponding elements from
				# <list>_upper_partstaff to <list>  
				if is_lower_partstaff:
					if j in clef_change_bars:
						clefs.append(clefs_upper_partstaff[clef_change_bars.index(j)])
					if j in key_sig_change_bars:
						key_sigs.append(key_sigs_upper_partstaff[key_sig_change_bars.index(j)])			
					if j in meter_change_bars:
						meters.append(meters_upper_partstaff[meter_change_bars.index(j)])

				for item in measure:
					# TODO if is lower_partstaff: if empty measure, copy from upper; else add (5a)
					# TODO or do not do lower_partstaff (5b)
					if isinstance(item, m21.clef.Clef):
						if is_non_divided or is_upper_partstaff:
							clefs.append([item.sign, item.line, item.octaveChange, j])
					elif isinstance(item, m21.key.Key):
						if is_non_divided or is_upper_partstaff:
							key_sigs.append([item.name, j])
					elif isinstance(item, m21.meter.TimeSignature):
						if is_non_divided or is_upper_partstaff:
							meters.append([item, j])
						if not item.ratioString in all_meter_strings:
							all_meter_strings.append(item.ratioString)
					elif isinstance(item, m21.note.Note):
						# First note in sequence of tied notes: add note to list
						dur = item.duration.quarterLength/4.0
						dur = Fraction.from_float(dur)

						# If last added meter is triple
						# NB: use .ratioString because meters[-1][0].beatCount and meters[-1][0].beatCountName 
						# do not give the expected results
						numer = int(meters[-1][0].ratioString.split('/')[0])
#						if len(meters_first_part) > 1 and 
						if numer % 3 == 0:
							dur = dur * Fraction(2, 3)

						if item.tie == None or item.tie.type == 'start':
							# If dur is an integer, add an int; else, add a fraction
							if dur % 1 == 0:
								dur_to_add = int(dur.numerator / dur.denominator)
							else:
								dur_to_add = dur	
#							if not item.tie == None:
#								print(dur_to_add)
					
							notes.append([item.pitch, item.pitch.midi, dur_to_add, j, meters[-1][0]])
						# Middle or last note in sequence of tied notes: increment duration in last element of list
						elif item.tie.type == 'continue' or item.tie.type == 'stop':
							prev_dur = notes[-1][2] + dur
#							if item.tie.type == 'stop':
#								print(prev_dur)
						
							# If prev_dur is an integer, set as int; else, set as Fraction
							if prev_dur % 1 == 0:
#								if item.tie.type == 'stop':
#									print('dur =',dur)
								dur_to_add = int(prev_dur.numerator / prev_dur.denominator)
							else:
								dur_to_add = prev_dur
							notes[-1][2] = dur_to_add

#						if i == 0:
#							print(j, item.nameWithOctave, dur)	
					elif isinstance(item, m21.note.Rest):
						dur = item.duration.quarterLength/4.0 
						dur = Fraction.from_float(dur)
						# If last added meter is triple
						# NB: use .ratioString because meters[-1][0].beatCount and meters[-1][0].beatCountName 
						# do not give the expected results
						numer = int(meters[-1][0].ratioString.split('/')[0])					
#						if len(meters_first_part) > 1 and numer % 3 == 0:
						if numer % 3 == 0:	
							dur = dur * Fraction(2, 3)
						rests.append([item, dur, j, meters[-1][0]])

			notes_df = pd.DataFrame(np.asarray(notes), columns=notes_header)
#			print('---> notes:')
#			print(notes_df.to_string())
			
			rests_df = pd.DataFrame(np.asarray(rests), columns=rests_header)
			total_note_duration = notes_df['duration'].sum()
			total_rest_duration = rests_df['duration'].sum()
			total_part_duration = total_note_duration + total_rest_duration 

#			print(len_piece) 

#			if (total_part_duration != len_piece):
#				print('part', part.partName, ': sum of all notes and rest not equal to piece length')
#				print('piece length =', len_piece, '; sum of all notes and rests =', total_part_duration)
	
#			if part.id == 'P1-Staff2':
#				print(notes_df.to_string())

			# Set upper partstaff lists
			if is_upper_partstaff:
				clefs_upper_partstaff = clefs
				key_sigs_upper_partstaff = key_sigs
				meters_upper_partstaff = meters
				# Also set notes_upper_partstaff_df
				notes_upper_partstaff = notes
				notes_upper_partstaff_df = notes_df
			# Clear upper part staff lists
			elif is_lower_partstaff:
				# Concatenate the DataFrames representing the upper and lower partstaffs
				notes = notes_upper_partstaff + notes
				notes_df = pd.concat([notes_upper_partstaff_df, notes_df], ignore_index=True)

				# Reset
				clefs_upper_partstaff = []
				key_sigs_upper_partstaff = []
				meters_upper_partstaff = []
				notes_upper_partstaff = []
				notes_upper_partstaff_df = None

			# 2. Create durs and durs_df, containing the length of time spent on each pitch in the part
			durs = np.column_stack((pitch_range_note, pitch_range_midi, np.zeros(len(pitch_range_midi))))
			for item in notes:
				# np.where returns a tuple, the first element of which is a single-element array (as the notes are unique)
				durs_ind = np.where(pitch_range_midi == item[notes_header.index('pitch')])[0][0]
				durs[durs_ind][durs_header.index('duration')] += item[notes_header.index('duration')]
			durs_df = pd.DataFrame(durs, columns=durs_header)
#			print(durs_df.to_string())
			max_dur_part = max(durs_df['duration'])
			if max_dur_part > max_dur_piece:
				max_dur_piece = max_dur_part

			# Save pitch countplot and durs barplot
			if is_non_divided or is_lower_partstaff or is_upper_without_lower:				
				plotting_data_per_part.append([durs_df, part.partName])

#				plot(durs_df, pitch_range_midi, diatonic_tick_labels, comp_piece, title, part.partName, 
#					add_counts, save_path, True, 'bar')
		
#		print(max_dur_piece)
		
		## end loop over parts

#		print(len_piece)

		# Plot all parts 
		dir_name = piece_name.lower()
		# Remove punctuation and replace spaces
		# For usage of translate() and maketrans() see https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string
		# For usage of arguments see https://stackoverflow.com/questions/41535571/how-to-explain-the-str-maketrans-function-in-python-3-6
		dir_name = dir_name.translate(str.maketrans('', '', string.punctuation))
		dir_name = dir_name.replace(' ', '_')		
		if composer is not None and ' ' in composer:
			composer_last_name = composer.split(' ')[-1]
		else:
			composer_last_name = composer

		dir_name = composer_last_name.lower() + '-' + dir_name
		save_path = os.path.join(path, 'img', dir_name)
		if not plot_averages:
			if not os.path.exists(save_path):
				os.makedirs(save_path)

		plotting_data_per_part_all_pieces.append(plotting_data_per_part)

		if not plot_averages:
			for part_data in plotting_data_per_part:
				durs_df = part_data[0]
				title = part_data[1]
				part_name = part_data[1]

				plot(durs_df, pitch_range_midi, diatonic_tick_labels, comp_piece, title, part_name, 
					max_dur_piece, add_counts, save_path, True, 'bar')

		all_max_dur.append(max_dur_piece)
		if max_dur_piece > max_dur_overall:
			max_dur_overall = max_dur_piece
			piece_with_max_dur = piece
		print()

	# end loop over pieces

	if plot_averages:
		print('==========================================')
		print('all_meter_strings')
		print(all_meter_strings)
		print('max_dur_overall')
		print(max_dur_overall)
		print('all_max_dur:')
		print(all_max_dur)
		print('piece_with_max_dur')
		print(piece_with_max_dur)
		print('pieces_with_illegal_part_names')
		print(pieces_with_illegal_part_names)

		print('= = = = = = = = = = = = = = = = = = = = = =')
		print('this should be 10:', str(len(plotting_data_per_part_all_pieces)))
		print('this should be  5:', str(len(plotting_data_per_part_all_pieces[0])))
#		print('this should be  5:', str(len(plotting_data_per_part_all_pieces[2])))
#		print('this should be  5:', str(len(plotting_data_per_part_all_pieces[3])))
#		print('this should be  8:', str(len(plotting_data_per_part_all_pieces[4])))
#		print('this should be  6:', str(len(plotting_data_per_part_all_pieces[5])))
#		print('this should be  6:', str(len(plotting_data_per_part_all_pieces[6])))
#		print('this should be  6:', str(len(plotting_data_per_part_all_pieces[7])))
#		print('this should be  5:', str(len(plotting_data_per_part_all_pieces[8])))
#		print('this should be  7:', str(len(plotting_data_per_part_all_pieces[9])))
		print('= = = = = = = = = = = = = = = = = = = = = =')

		# Average over voices
		# plotting_data_per_part_reorganised contains as many elements as there are parts, where each element 
		# contains the plotting data (a list containing the durs_df (at index 0) and the part name (at index 1)) 
		# for each instance of that part in all pieces
		part_names_avg = ['Mean', 'Contratenor 1', 'Contratenor 2', 'Tenor', 'Bassus']
		plotting_data_per_part_reorganised = {}
		for pn in part_names_avg:
			plotting_data_per_part_reorganised[pn] = []
	
		for plotting_data_per_part in plotting_data_per_part_all_pieces:
			for part_data in plotting_data_per_part:
				part_name = part_data[1].lower()
				if 'mean' in part_name:
					plotting_data_per_part_reorganised['Mean'].append(part_data)
				if 'contratenor 1' in part_name:
					plotting_data_per_part_reorganised['Contratenor 1'].append(part_data)
				if 'contratenor 2' in part_name:
					plotting_data_per_part_reorganised['Contratenor 2'].append(part_data)
				if 'tenor' in part_name and not 'contra' in part_name:
					plotting_data_per_part_reorganised['Tenor'].append(part_data)
				if 'bassus' in part_name:
					plotting_data_per_part_reorganised['Bassus'].append(part_data)

		print('this should be 15', len(plotting_data_per_part_reorganised['Mean']))
		print('this should be 10', len(plotting_data_per_part_reorganised['Contratenor 1']))
		print('this should be 10', len(plotting_data_per_part_reorganised['Contratenor 2']))
		print('this should be 12', len(plotting_data_per_part_reorganised['Tenor']))
		print('this should be 12', len(plotting_data_per_part_reorganised['Bassus']))

		save_path_avg = os.path.join(path, 'img', 'gibbons-10_pcs-avg')
		if not os.path.exists(save_path_avg):
			os.makedirs(save_path_avg)

		# Per part: sum and average duration over all part instances; determine max_dur_avg
		max_dur_avg = 0
		all_durs_part_df = []
		for item in plotting_data_per_part_reorganised.items():
#		for i, plotting_data_all_part_instances in enumerate(plotting_data_per_part_reorganised):
#		for i in range(0, len(plotting_data_per_part_reorganised)):
			part_name_avg = item[0] # key (part name)
			plotting_data_all_part_instances = item[1] # value 
#			part_name_avg = part_names_avg[i]
#			plotting_data_all_part_instances = plotting_data_per_part_reorganised[part_name_avg]
			durs_part_avg = np.zeros(len(pitch_range_midi))
			num_part_instances = len(plotting_data_all_part_instances)

			for part_inst in plotting_data_all_part_instances: # list
				durs_df = part_inst[0] # DataFrame
				part_name = part_inst[1] # string
				for j, dur in enumerate(durs_df['duration']): # Series
					durs_part_avg[j] = durs_part_avg[j] + dur

			# Average duration over all part instances
			for j, dur in enumerate(durs_part_avg):
				durs_part_avg[j] = dur / num_part_instances
				if durs_part_avg[j] > max_dur_avg:
					max_dur_avg = durs_part_avg[j]
	
			durs_part = np.column_stack((pitch_range_note, pitch_range_midi, durs_part_avg))
			durs_part_df = pd.DataFrame(durs_part, columns=durs_header)
			all_durs_part_df.append((durs_part_df, part_name_avg))

#			plot(durs_part_df, pitch_range_midi, diatonic_tick_labels, 'Gibbons, 10 pieces: average per voice', 
#				part_name_avg, part_name_avg, max(all_max_dur), add_counts, save_path_avg, True, 'bar')

		# Now that max_dur_avg is known, plot
		for (durs_part_df, part_name_avg) in all_durs_part_df:
			plot(durs_part_df, pitch_range_midi, diatonic_tick_labels, 'Orlando Gibbons - Average calculated from ten consort anthems in GB-Och MS Mus. 21', 
				part_name_avg, part_name_avg, max_dur_avg, add_counts, save_path_avg, True, 'bar')		

#	for item in all_part_names: 
#		print(item)piece_with_highest_count
	
#		O all true faithful hearts
#		- Mean, lower partstaff, b. 69-70: tie is not recognised, note counted twice
#		- Bassus, b. 77: ossia thing makes that part.partName and part.id are not the same (in other
#		               words, that the part is not non-divided - but there is only an upper partstaff)
#		- Contratenor 1, b. 60: rogue clef
#       - II, b. 60 and 62: rogue clefs  

#ax = sns.distplot(durs_df['duration (sb)']) #, order=pitch_range_midi)
#ax = sns.distplot(data=durs_df, x='duration (sb)') #, order=pitch_range_midi)
#ax.set_xticklabels(diatonic_tick_labels)
#plt.show()

if __name__ == '__main__':
	main()


exit(0)


print('clefs = ', clefs)
print('measures     :', len(measures))
print('notes        :', len(pitches))
print('rests        :', len(rests))
MIDI_pitches = [n.midi for n in pitches]
mean_pitch = statistics.mean(MIDI_pitches)
mean_pitch_class = round(mean_pitch) % 12
print('average pitch:', m21.pitch.Pitch(mean_pitch_class), '(' + str(mean_pitch) + ', rounded)')
median_pitch = statistics.median(MIDI_pitches)
median_pitch_class = round(median_pitch) % 12
print('median pitch :', m21.pitch.Pitch(median_pitch_class), '(' + str(median_pitch) + ')')
min_pitch_class = min(MIDI_pitches) % 12
max_pitch_class = max(MIDI_pitches) % 12
low_name = pitches[MIDI_pitches.index(min(MIDI_pitches))]
hi_name =  pitches[MIDI_pitches.index(max(MIDI_pitches))]
print('range        :', low_name.nameWithOctave + '-' + hi_name.nameWithOctave)
print('occurrences  :', str(pitches.count(low_name)) + ', ' + str(pitches.count(hi_name)))
#print('three most common notes')