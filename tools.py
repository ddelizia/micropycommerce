import argparse
from utils.crypto import encrypt_file, decrypt_file

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--file', help='File to decrypt', required=True)
parser.add_argument('--key', help='Encryption/Decryption key', required=True)
parser.add_argument(
    '--encrypt', help='Encrypt current file',
    action='store_true')
parser.add_argument(
    '--decrypt', help='Decrypt current file', action='store_true')
args = parser.parse_args()

print(args)

if args.encrypt is True:
    encrypt_file(args.key, args.file)
elif args.decrypt is True:
    decrypt_file(args.key, args.file)
else:
    print('Specify --encrypt or --decrypt')
