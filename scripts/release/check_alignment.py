#!/usr/bin/env python3
"""Equivalent of `zipalign -c -P 16 4 <apk>`: checks that every stored (uncompressed) entry of an APK starts on
a 4-byte boundary and that uncompressed native libraries (.so) start on a 4096-byte page boundary (16 KB
alignment is reported separately). Exit code 1 if the APK is not aligned.
"""
import struct
import sys
import zipfile


def main(path):
    problems, so_16k, so_total = [], 0, 0
    with open(path, 'rb') as handle, zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            handle.seek(info.header_offset)
            header = handle.read(30)
            if header[:4] != b'PK\x03\x04':
                problems.append(f'{info.filename}: en-tête local invalide')
                continue
            name_length, extra_length = struct.unpack('<HH', header[26:30])
            data_offset = info.header_offset + 30 + name_length + extra_length
            if info.compress_type != zipfile.ZIP_STORED:
                continue
            if info.filename.endswith('.so'):
                so_total += 1
                so_16k += data_offset % 16384 == 0
                if data_offset % 4096:
                    problems.append(f'{info.filename}: décalage {data_offset} non aligné sur 4096')
            elif data_offset % 4:
                problems.append(f'{info.filename}: décalage {data_offset} non aligné sur 4')
    for problem in problems:
        print('NON ALIGNÉ', problem)
    print(f'{path}: {"aligné" if not problems else "NON ALIGNÉ"} ; bibliothèques natives non compressées alignées 16 Ko : {so_16k}/{so_total}')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
