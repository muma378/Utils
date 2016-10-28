import sys
import chardet
from dp.core.base.traverse import traverser

def append(mergefile, dirname):
	for filepath, _ in traverser(dirname, '', target='.txt'):
		with open(filepath) as f:
			raw_content = f.read()
			coding = chardet.detect(raw_content[:4000])['encoding']
			if coding != 'utf-8':
				try:
					raw_content = raw_content.decode(coding).encode('utf-8')
				except UnicodeDecodeError as e:
					print('decode failed for {0}'.format(filepath))
					continue
		with open(mergefile, 'a') as m:
			m.write(raw_content)



if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("please enter at least 2 arguments")
		sys.exit()

	mergefile = 'merge.txt'
	for path in sys.argv[1:]:
		append(mergefile, path	)