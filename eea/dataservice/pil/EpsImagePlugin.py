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
from PIL.EpsImagePlugin import PSFile, i32, split, field

logger = logging.getLogger('eea.dataservice.pil.EpsImagePlugin')

def Ghostscript(tile, size, fp, dpi=None):
    """Render an image using Ghostscript (Unix only)"""

    # Unpack decoder tile
    _decoder, tile, offset, data = tile[0]
    length, bbox = data

    import tempfile, os

    efile = tempfile.mktemp()

    # Build ghostscript command
    try:
        dpi = int(dpi)
    except (TypeError, ValueError):
        dpi = 0

    if not dpi:
        command = ["gs",
                   "-q",                    # quite mode
                   "-g%dx%d" % size,        # set output geometry (pixels)
                   "-dNOPAUSE -dSAFER",     # don't pause between pages
                   "-sDEVICE=ppmraw",       # ppm driver
                   "-sOutputFile=%s" % efile,# output file
                   "- >/dev/null 2>/dev/null"]
    else:
        command = ["gs",
                   "-q",                    # quite mode
                   "-r%d" % dpi,            # set output resolution (pixels)
                   "-dEPSCrop",             # crop
                   "-dNOPAUSE -dSAFER",     # don't pause between pages
                   "-sDEVICE=ppmraw",       # ppm driver
                   "-sOutputFile=%s" % efile,# output file
                   "- >/dev/null 2>/dev/null"]

    command = " ".join(command)

    # push data through ghostscript
    try:
        gs = os.popen(command, "w")

        if not dpi:
            # adjust for image origin
            if bbox[0] != 0 or bbox[1] != 0:
                gs.write("%d %d translate\n" % (-bbox[0], -bbox[1]))

        fp.seek(offset)
        while length > 0:
            s = fp.read(8192)
            if not s:
                break
            length = length - len(s)
            gs.write(s)
        status = gs.close()
        if status:
            raise IOError("gs failed (status %d)" % status)
        im = Image.core.open_ppm(efile)
    finally:
        try:
            os.unlink(efile)
        except OSError, err:
            logger.debug(err)
    return im

class EpsImageFile(PILEpsImageFile):
    """EPS File Parser for the Python Imaging Library"""

    def _open(self):
        """ Open
        """
        # FIX ME: should check the first 512 bytes to see if this
        # really is necessary (platform-dependent, though...)

        fp = PSFile(self.fp)

        # HEAD
        s = fp.read(512)
        if s[:4] == "%!PS":
            offset = 0
            fp.seek(0, 2)
            length = fp.tell()
        elif i32(s) == 0xC6D3D0C5L:
            offset = i32(s[4:])
            length = i32(s[8:])
            fp.seek(offset)
        else:
            raise SyntaxError, "not an EPS file"

        fp.seek(offset)

        box = None

        self.mode = "RGB"
        self.size = 1, 1 # FIX ME: huh?

        #
        # Load EPS header

        s = fp.readline()

        while s:

            if len(s) > 255:
                raise SyntaxError, "not an EPS file"

            if s[-2:] == '\r\n':
                s = s[:-2]
            elif s[-1:] == '\n':
                s = s[:-1]

            try:
                m = split.match(s)
            except re.error, v:
                raise SyntaxError, "not an EPS file"

            if m:
                k, v = m.group(1, 2)
                self.info[k] = v
                if k == "BoundingBox":
                    try:
                        # Note: The DSC spec says that BoundingBox
                        # fields should be integers, but some drivers
                        # put floating point values there anyway.
                        box = [int(float(x)) for x in v.split()]
                        self.size = box[2] - box[0], box[3] - box[1]
                        offset = 0
                        self.tile = [("eps", (0, 0) + self.size, offset,
                                      (length, box))]
                    except Exception, err:
                        logger.exception(err)
            else:

                m = field.match(s)

                if m:
                    k = m.group(1)
                    if k == "EndComments":
                        break
                    if k[:8] == "PS-Adobe":
                        self.info[k[:8]] = k[9:]
                    else:
                        self.info[k] = ""
                else:
                    raise IOError, "bad EPS header"

            s = fp.readline()

            while s.startswith('%A'):
                s = fp.readline()

            if s[:1] != "%":
                break


        #
        # Scan for an "ImageData" descriptor

        while s[0] == "%":

            if len(s) > 255:
                raise SyntaxError, "not an EPS file"

            if s[-2:] == '\r\n':
                s = s[:-2]
            elif s[-1:] == '\n':
                s = s[:-1]

            if s[:11] == "%ImageData:":

                [x, y, bi, mo,
                 _z3, _z4, en, eid] = str.split(s[11:], maxsplit=7)

                x = int(x)
                y = int(y)
                bi = int(bi)
                mo = int(mo)

                en = int(en)

                if en == 1:
                    decoder = "eps_binary"
                elif en == 2:
                    decoder = "eps_hex"
                else:
                    break
                if bi != 8:
                    break
                if mo == 1:
                    self.mode = "L"
                elif mo == 2:
                    self.mode = "LAB"
                elif mo == 3:
                    self.mode = "RGB"
                else:
                    break

                if eid[:1] == eid[-1:] == '"':
                    eid = eid[1:-1]

                # Scan forward to the actual image data
                while 1:
                    s = fp.readline()
                    if not s:
                        break
                    if s[:len(eid)] == eid:
                        self.size = x, y
                        self.tile2 = [(decoder,
                                       (0, 0, x, y),
                                       fp.tell(),
                                       0)]
                        return

            s = fp.readline()
            if not s:
                break

        if not box:
            raise IOError, "cannot determine EPS bounding box"

    def load(self):
        """ Load
        """
        # Load EPS via Ghostscript
        if not self.tile:
            return

        dpi = getattr(self, 'dpi', None)
        self.im = Ghostscript(self.tile, self.size, self.fp, dpi=dpi)
        self.mode = self.im.mode
        self.size = self.im.size
        self.tile = []
