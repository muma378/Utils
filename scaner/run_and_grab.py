import sys
import os
import re
import subprocess

from PIL import ImageGrab

screen_size = (1920, 1080)
window_coord = (1168, 1056, 1920, 552)

def run(prog, url):
    try:
        print "python {0} {1}".format(prog, url)
        subprocess.check_call(["python", prog, url])
        return None
    except subprocess.CalledProcessError as e:
        return url

# std_coord is metered from the left-bottom corner
# but grab is from the left-top corner
def grab(std_coord, name):
    window = (std_coord[0], screen_size[1]-std_coord[1], std_coord[2], screen_size[1]-std_coord[3])
    im = ImageGrab.grab(window)
    im.save(name)

def get_urls(filename):
    urls =[]
    with open(filename, 'r') as f:
        for line in f:
            urls.append(line.strip())
    return urls

def main(urls_file, save_path):
    failed = []
    urls = get_urls(urls_file)
    for url in urls:
        failed_url = run("iis_shortname_scan.py", url)
        if failed_url:
            failed.append(failed_url)
            continue
        domain = re.match("http://w*\.?([^/]*).*", url)
        if domain:
            name = domain.group(1)
        else:
            name = url
        
        name = name.replace('.', '_').replace('/', '_').replace(':', '') + '.bmp'
        name = os.path.join(save_path, name)
        grab(window_coord, name)
    
    if failed:
        print "failed request: \n"
        for url in failed:
            print url + "\n"

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
