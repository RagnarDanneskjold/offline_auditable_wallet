# an abridged version of the code at
# https://raw.github.com/jackjack-jj/pywallet/75884a22c12660828401b89eac0462cfbc063b92/pywallet.py

# licensing murky, though new version under development as of Sept 2013
# was going to be GPLv3
# not much here, so no big deal, all of this could be re-written
# documented here:
# https://en.bitcoin.it/wiki/Technical_background_of_Bitcoin_addresses

# Mark Jenkins changed a few things in here to make this work with python3
# got rid of long int suffixes e.g. "0L" and cleaned up use of bytes vs
# strings and int to byte conversion

pywversion="2.1.6"

import hashlib

from ecdsa.six import int2byte as int_to_byte

from .base58 import b58encode, b58decode

addrtype = 0

def i2o_ECPublicKey(pkey, compressed=False):
	# public keys are 65 bytes long (520 bits)
	# 0x04 + 32-byte X-coordinate + 32-byte Y-coordinate
	# 0x00 = point at infinity, 0x02 and 0x03 = compressed, 0x04 = uncompressed
	# compressed keys: <sign> <x> where <sign> is 0x02 if y is even and 0x03 if y is odd
	if compressed:
		if pkey.pubkey.point.y() & 1:
			key = '03' + '%064x' % pkey.pubkey.point.x()
		else:
			key = '02' + '%064x' % pkey.pubkey.point.x()
	else:
		key = '04' + \
			'%064x' % pkey.pubkey.point.x() + \
			'%064x' % pkey.pubkey.point.y()

	return bytes.fromhex(key)

# bitcointools hashes and base58 implementation

def hash_160(public_key):
	md = hashlib.new('ripemd160')
	md.update(hashlib.sha256(public_key).digest())
	return md.digest()

def public_key_to_bc_address(public_key, v=None):
	if v==None:
		v=addrtype
	h160 = hash_160(public_key)
	return hash_160_to_bc_address(h160, v)

def hash_160_to_bc_address(h160, v=None):
	if v==None:
		v=addrtype
	vh160 = int_to_byte(v) + h160
	h = Hash(vh160)
	addr = vh160 + h[0:4]
	return b58encode(addr)

def Hash(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def EncodeBase58Check(secret):
	hash = Hash(secret)
	return b58encode(secret + hash[0:4])

def DecodeBase58Check(sec):
	vchRet = b58decode(sec, None)
	secret = vchRet[0:-4]
	csum = vchRet[-4:]
	hash = Hash(secret)
	cs32 = hash[0:4]
	if cs32 != csum:
		return None
	else:
		return secret

def SecretToASecret(secret, compressed=False):
	prefix = int_to_byte((addrtype+128)&255)
	if addrtype==48:  #assuming Litecoin
		prefix = int_to_byte(128)
	vchIn = prefix + secret
	if compressed: vchIn += b'\01'
	return EncodeBase58Check(vchIn)

def ASecretToSecret(sec):
	vch = DecodeBase58Check(sec)
	if not vch:
		return False
	if vch[0] != (addrtype+128)&255:
		print( 'Warning: adress prefix seems bad (%d vs %d)'%(
                        vch[0], (addrtype+128)&255) )
	return vch[1:]

def GetPubKey(pkey, compressed=False):
	return i2o_ECPublicKey(pkey, compressed)

def is_compressed(sec):
	b = ASecretToSecret(sec)
	return len(b) == 33
