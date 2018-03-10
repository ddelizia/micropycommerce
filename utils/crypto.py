import pyAesCrypt


def encrypt_file(password, in_filename, out_filename=None, chunksize=64 * 1024):
    final_outfilename = out_filename
    if final_outfilename is None:
        final_outfilename = in_filename + '.enc'
    pyAesCrypt.encryptFile(
        in_filename, final_outfilename, password, chunksize)


def decrypt_file(password, in_filename, out_filename=None, chunksize=64 * 1024):
    final_outfilename = out_filename
    if final_outfilename is None:
        if in_filename.endswith('.enc'):
            final_outfilename = in_filename[:-4]
    pyAesCrypt.decryptFile(
        in_filename, final_outfilename, password, chunksize)



