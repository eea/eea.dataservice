"""
Override PIL EPS plugin to:

- Support newer EPS formats

  Below is a fix of EPS image plugin from PIL so now can handle
  EPS files generated with different applications.

  The 2 lines of code below are the fix for case EPS files are generates
  using Adobe Freehand. We will keep this commented as at the moment we dont
  have any usecase.

  from PIL.EpsImagePlugin import EpsImageFile, PSFile, i32, field
  split = re.compile(r"^%[%!\\w]([^:]*):[ \t]*(.*)[ \t]*$")

- Support bigger resolution

By default PIL EPS plugin opens .eps files at a lower resolution. Fix this by
adding dpi param to save function.
"""
import logging
import re
from PIL import Image
from PIL.EpsImagePlugin import EpsImageFile as PILEpsImageFile
from PIL.EpsImagePlugin import PSFile, i32, split, field, gs_windows_binary

logger = logging.getLogger('eea.dataservice.pil.EpsImagePlugin')


def Ghostscript(tile, size, fp, scale=1, dpi=None):
    """Render an image using Ghostscript"""

    # Unpack decoder tile
    decoder, tile, offset, data = tile[0]
    length, bbox = data

    import os
    import subprocess
    import tempfile

    out_fd, outfile = tempfile.mkstemp()
    os.close(out_fd)

    infile_temp = None
    if hasattr(fp, 'name') and os.path.exists(fp.name):
        infile = fp.name
    else:
        in_fd, infile_temp = tempfile.mkstemp()
        os.close(in_fd)
        infile = infile_temp

        # ignore length and offset!
        # ghostscript can read it
        # copy whole file to read in ghostscript
        with open(infile_temp, 'wb') as f:
            # fetch length of fp
            fp.seek(0, 2)
            fsize = fp.tell()
            # ensure start position
            # go back
            fp.seek(0)
            lengthfile = fsize
            while lengthfile > 0:
                s = fp.read(min(lengthfile, 100*1024))
                if not s:
                    break
                lengthfile -= len(s)
                f.write(s)

    # Build ghostscript command
    try:
        dpi = int(dpi)
    except (TypeError, ValueError):
        dpi = 0

    if not dpi:
        # Hack to support hi-res rendering
        scale = int(scale) or 1
        # orig_size = size
        # orig_bbox = bbox
        size = (size[0] * scale, size[1] * scale)
        # resolution is dependent on bbox and size
        res = (float((72.0 * size[0]) / (bbox[2]-bbox[0])),
               float((72.0 * size[1]) / (bbox[3]-bbox[1])))
        # print("Ghostscript", scale, size, orig_size, bbox, orig_bbox, res)
        # Build ghostscript command
        command = ["gs",
                   "-q",                         # quiet mode
                   "-g%dx%d" % size,             # set output geometry (pixels)
                   "-r%fx%f" % res,              # set input DPI (dots per inch)
                   "-dNOPAUSE -dSAFER",          # don't pause between pages,
                                                 # safe mode
                   "-sDEVICE=ppmraw",            # ppm driver
                   "-sOutputFile=%s" % outfile,  # output file
                   "-c", "%d %d translate" % (-bbox[0], -bbox[1]),
                                                 # adjust for image origin
                   "-f", infile,                 # input file
                   ]
    else:
        command = ["gs",
                   "-q",                        # quite mode
                   "-r%d" % dpi,                # set output resolution (pixels)
                   "-dEPSCrop",                 # crop
                   "-dNOPAUSE -dSAFER",         # don't pause between pages
                   "-sDEVICE=ppmraw",           # ppm driver
                   "-sOutputFile=%s" % outfile, # output file
                   "-f", infile,                # input file
                   "- >/dev/null 2>/dev/null"]

    if gs_windows_binary is not None:
        if not gs_windows_binary:
            raise WindowsError('Unable to locate Ghostscript on paths')
        command[0] = gs_windows_binary

    # push data through ghostscript
    try:
        gs = subprocess.Popen(command, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        gs.stdin.close()
        status = gs.wait()
        if status:
            raise IOError("gs failed (status %d)" % status)
        im = Image.core.open_ppm(outfile)
    finally:
        try:
            os.unlink(outfile)
            if infile_temp:
                os.unlink(infile_temp)
        except:
            pass

    return im


class EpsImageFile(PILEpsImageFile):
    """EPS File Parser for the Python Imaging Library"""

    def load(self, scale=4):
        """ Load
        """
        # Load EPS via Ghostscript
        if not self.tile:
            return

        dpi = getattr(self, 'dpi', None)
        self.im = Ghostscript(self.tile, self.size, self.fp,
            scale=scale, dpi=dpi)
        self.mode = self.im.mode
        self.size = self.im.size
        self.tile = []
