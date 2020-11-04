import numpy as np
from hexutils import *
from attack import *


def key_gen(i, k):
	l_k = k.shape[0]
	key = np.zeros((l_k,), dtype=int)

	for j in range(1, l_k + 1):
		index = ((5 * i + j - 1) % l_k) + 1  # the formula in the slide is 1-indexed
		key[j - 1] = k[index - 1]

	return key


def lin_f(k, i, y):
	l = y.shape[0]
	w = np.zeros((l + 1,), dtype=int)  # w is starts from index 1 for easier computation
	for j in range(1, l + 1):
		if j <= l / 2:
			w[j] = y[j - 1] ^ k[4 * j - 3 - 1]
		else:
			w[j] = y[j - 1] ^ k[4 * j - 2 * l - 1]
	return w[1:]


def near_lin_f(k, i, y):
	l = y.shape[0]
	w = np.zeros((l + 1,), dtype=int)  # w is starts from index 1 for easier computation
	for j in range(1, l + 1):
		if j <= l / 2:
			t = y[2 * j - 1 - 1] | k[2 * j - 1 - 1] | k[2 * j - 1] | k[4 * j - 2 - 1]
			w[j] = y[j - 1] ^ (k[4 * j - 3 - 1] & t)
		else:
			t = k[4 * j - 2 * l - 1 - 1] | k[2 * j - 1 - 1] | k[2 * j - 1] | [2 * j - l - 1]
			w[j] = y[j - 1] ^ (k[4 * j - 2 * l - 1] & t)
	return w[1:]


def non_lin_f(k, i, y):
	l = y.shape[0]
	w = np.zeros((l + 1,), dtype=int)  # w starts from index 1 for easier computation
	for j in range(1, l + 1):
		if j <= l / 2:
			t = (y[2 * j - 1 - 1] & k[2 * j - 1]) | k[4 * j - 1]
			w[j] = (y[j - 1] & k[2 * j - 1 - 1]) | t
		else:
			t = (k[4 * j - 2 * l - 1 - 1] & k[2 * j - 1]) | y[2 * j - l - 1]
			w[j] = (y[j - 1] & k[2 * j - 1 - 1]) | t
	return w[1:]


def encrypt(u, k, r, l, f):
	y = u[:(l // 2)]
	z = u[(l // 2):]

	for i in range(r):
		round_key = key_gen(i + 1, k)
		w = f(round_key, i, y)
		v = np.bitwise_xor(w, z)
		z = y
		y = v

	x = np.append(z, y)  # wrong way around since we did one more T in the for loop
	return x


def decrypt(x, k, r, l, f):
	y = x[:(l // 2)]
	z = x[(l // 2):]

	for i in range(r):
		round_key = key_gen(r - i, k)  # inverted key sequence
		w = f(round_key, i, y)
		v = np.bitwise_xor(w, z)
		z = y
		y = v

	u = np.append(z, y)  # wrong way around since we did one more T in the for loop
	return u


def most_frequent(List):
	return max(set(List), key=List.count)


def main():
	# ----- TASK 1 AND 2 ----
	print("Linear Feistel")
	k = strhex_to_bin_array('0x80000000', 32)
	u = strhex_to_bin_array('0x80000000', 32)

	x = encrypt(u, k, 17, 32, lin_f)
	uu = decrypt(x, k, 17, 32, lin_f)

	print("Encrypted text:")
	# print(x)
	print(bin_array_to_strhex(x))
	print("Decrypted text:")
	# print(uu)
	print(bin_array_to_strhex(uu))

	# ----- TASK 3 ----
	print("\nFind linear matrices")
	a, b = find_mat(encrypt, 32, lin_f)

	print("matrix A:")
	print(a)
	print("matrix B:")
	print(b)

	# ----- TASK 4 ----
	print("\ntest KPA attack")
	tk = strhex_to_bin_array('0x12340050', 32)
	tx = encrypt(u, tk, 17, 32, lin_f)
	kk = find_key_kpa(a, b, u, tx)
	print("key: ", bin_array_to_strhex(kk))

	print("KPA attack on file data")
	file1 = open('data/KPApairsVancouver_linear.hex', 'r')
	lines = file1.readlines()
	for line in lines:
		l = line.split("\t")
		p_txt = strhex_to_bin_array("0x" + l[0], 32)
		c_txt = strhex_to_bin_array("0x" + l[1], 32)
		kk = find_key_kpa(a, b, p_txt, c_txt)
		print("key: ", bin_array_to_strhex(kk))

	# ----- TASK 5 ----
	print("\nNearly-linear Feistel")
	k = strhex_to_bin_array('0x87654321', 32)
	u = strhex_to_bin_array('0x12345678', 32)

	x = encrypt(u, k, 5, 32, near_lin_f)
	uu = decrypt(x, k, 5, 32, near_lin_f)

	print("Encrypted text:")
	print(bin_array_to_strhex(x))
	print("Decrypted text:")
	print(bin_array_to_strhex(uu))

	# ----- TASK 7 ----
	print("\nNon-linear Feistel")
	k = strhex_to_bin_array('0x369C', 16)
	u = strhex_to_bin_array('0x0000', 16)

	x = encrypt(u, k, 13, 16, non_lin_f)
	uu = decrypt(x, k, 13, 16, non_lin_f)

	print("Encrypted text:")
	print(bin_array_to_strhex(x))
	print("Decrypted text:")
	print(bin_array_to_strhex(uu))

	# ----- TASK 8 ----
	print("\nMeet in the Middle attack")
	print("Keypairs candidates")
	total_matches = []
	file1 = open('data/KPApairsVancouver_non_linear.hex', 'r')
	#file1 = open('data/KPApairsTest_non_linear.hex', 'r')
	lines = file1.readlines()

	l = lines[0].split("\t")
	p_txt = strhex_to_bin_array("0x" + l[0], 16)
	c_txt = strhex_to_bin_array("0x" + l[1], 16)

	# use meet_in_the_middle if you are feeling lucky today
	# or use meet_in_the_middle_sequential if you want to be sure to get the keys
	matches = meet_in_the_middle(2 ** 16, 2 ** 16, encrypt, decrypt, p_txt, c_txt, non_lin_f, 16)
	correct = []

	if not matches:
		print("no matches found")
	else:
		for keypair in matches:
			#if keypair[0] == '0x1234':
			#	print('the key is present: ', keypair)

			works = 0
			for line in lines:
				l = line.split("\t")
				p_txt = strhex_to_bin_array("0x" + l[0], 16)
				c_txt = strhex_to_bin_array("0x" + l[1], 16)
				if np.array_equal(encrypt(encrypt(p_txt, strhex_to_bin_array(keypair[0], 16), 13, 16, non_lin_f),
										  strhex_to_bin_array(keypair[1], 16), 13, 16, non_lin_f), c_txt):
					works += 1
			# print("Works for {} texts".format(works))
			correct.append(works)

	max_correct = max(correct)
	index_correct = correct.index(max_correct)
	keys_correct = matches[index_correct]
	print("Best keypair {} with {} matches".format(keys_correct, max_correct))
	# print(np.argmax(np.array(correct)).shape)
	(unique, counts) = np.unique(correct, return_counts=True)
	frequencies = np.asarray((unique, counts)).T
	print("Histogram of matches for keypairs:")
	print(frequencies)


if __name__ == "__main__":
	main()
