# import gevent
import grequests
import requests
from pprint import pprint
import os
import os.path
from tqdm import tqdm
from PIL import Image
from StringIO import StringIO



def get_synsets(idfile="wnids.txt"):
  WNID_TO_SYNSET = "http://www.image-net.org/api/text/wordnet.synset.getwords?wnid={}"
  wanted = [l.strip() for l in open(idfile) if l.strip() is not '' and not l.startswith("#")]
  with open("fgo_synsets.txt", 'w') as fp:
    for wnid in wanted:
      l = ", ".join(requests.get(WNID_TO_SYNSET.format(wnid)).text.split("\n")[:-1])
      fp.write("{} {}\n".format(wnid, l))


def download_images(wnidfile="fgo_synsets.txt", folder="imagenet"):
  URL = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid={}"
  wnids = [l.strip().split()[0] for l in open(wnidfile)]
  for wnid in wnids:
    print("getting %s (%d/%d)" % (wnid, wnids.index(wnid)+1, len(wnids)))
    try:
      os.makedirs(os.path.join(folder, wnid))
    except: pass
    urls = [_.strip() for _ in requests.get(URL.format(wnid)).text.split("\r")]
    jobs = [grequests.get(url) for url in urls]
    n_images, curr = 10, 0
    pbar = tqdm(total=n_images)
    for res in grequests.imap(jobs, size=3):
      if "unavailable" in res.url: continue
      try:
        im = Image.open(StringIO(res.content))
        if im.width < 128 or im.height < 128: continue
        filename = res.url.replace("/","_")
        im.save(os.path.join(folder, wnid, filename))
        pbar.update()
        curr += 1
        if curr >= n_images: break
      except:
        continue


if __name__ == '__main__':
  download_images()
