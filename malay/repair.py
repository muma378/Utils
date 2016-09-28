import sys
import re
from core.base import regexp
from core.base.traverse import traverse, traverser
from core.base.load import load_csv



class AnnotationSubBuilder(regexp.SubBuilder):
	"""to substitute annotations in malay text"""
	def __init__(self):
		super(AnnotationSubBuilder, self).__init__()
		
	# differs from SubBuilder, it escapes patterns in rules
	def build_rules(self, rules):
		escape_braces = lambda x: x.replace(r"[", r"\[").replace(r"]", r"\]")
		escaped_rules = []
		for origin, repl in rules:
			if origin == repl:
				continue
			escaped_rules.append((escape_braces(origin), repl))
		super(AnnotationSubBuilder, self).build_rules(escaped_rules)


class AnnotationMatchBuilder(regexp.MatchBuilder):
	"""estracts all annotation"""
	def __init__(self):
		super(AnnotationMatchBuilder, self).__init__()

	def build_rules(self, rules):
		self.regex.rules = re.compile("\[.+?\]")

	def build_parser(self):
		self.regex.parse = lambda r, t: r.findall(t)		


def sub_directory_by_csv(csv_file, root):
	replace_map = map(lambda x: (x[0].strip(),  x[1].strip()), load_csv(csv_file))
	import pdb;pdb.set_trace()
	rd = regexp.RegexDirector(AnnotationSubBuilder())
	regex_proc = rd.construct(replace_map).get_regex_proc()

	def proc_adaptor(src_file, _):
		regex_proc.process_file(src_file)

	traverse(root, '', proc_adaptor, target='.txt')

def collect_directory_annotations(root):
	rd = regexp.RegexDirector(AnnotationMatchBuilder())
	regex_proc = rd.construct(None).get_regex_proc()
	annotations = set()
	for src_file, _  in traverser(root, '', '.txt'):
		annotations.update(regex_proc.process_file(src_file))

	print annotations


if __name__ == '__main__':
	csv_file = sys.argv[1]
	root = sys.argv[2]
	sub_directory_by_csv(csv_file, root)
	# collect_directory_annotations(root)

