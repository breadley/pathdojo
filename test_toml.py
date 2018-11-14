# can be multiline. Use backslashes at the end of a line to indicate new line. (\)
description = '''

Monomorphic cells with granular cytoplasm, with Crooke's Hyaline (intermediate filaments that aggregate around the nucleus as cytopathic response to ACTH). ACTH is sparsely granulated, which increases local recurrence risk. Crooke's adenoma has a high Ki-67 and all cells stain positive for ACTH.

'''

# must be one line, in format ihc = {ihc1='+',ihc2='-'}.
immunohistochemistry = {ACTH='+',Cam5.2='+',T-Pit='+'}

genetics = '''
T-Pit transcription factor
'''

# can be multiline, as strings separated by commas.
differentials = [
'pituitary_adenoma_densely_granulated_corticotroph',
'crookes_adenoma'
]
