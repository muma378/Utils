from distutils.core import setup
import py2exe

setup(name='validate_textgrids',
	version='2.1',
	description='To validate the legality of textgrids',
	author='Xiao Yang',
	author_email='xiaoyang0117@gmail.com',
	console=["textgrid.py"],
	options={
		'py2exe':{
			'include': []
		}

	})
