import wave
import os
import sys
from traverse import traverse

def pcm2wav(srcfn, dstfn):
    dirname = os.path.dirname(dstfn)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(srcfn,'rb') as pcmf:
        pcmdata = pcmf.read()   
    nframes = os.path.getsize(srcfn) / 2
    
    wavf = wave.open(dstfn.replace('.pcm', '.wav'),'wb')    
    wavf.setparams((1, 2, 16000, nframes, 'NONE', 'not compressed'))
    wavf.writeframes(pcmdata)
    wavf.close()


if __name__ == '__main__':
    original = sys.argv[1]
    traverse(original, 'converted', pcm2wav, target='.pcm')