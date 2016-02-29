from distutils.core import setup
import py2exe


setup(
	name='sync_info',
	version='1.0',
	description='To sync info in hk server',
	author='Xiao Yang',
	author_email='xiaoyang0117@gmail.com',
	console=["sync_hkserv_info.py"],
	options={
		'py2exe':
		{
			'includes': ['lxml.etree', 'lxml._elementpath']
		}
	}
	)
