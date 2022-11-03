from .RTBox import RTBox as Box

def revbits(n):
	'''
	Reverses the digits of an 8-bit binary number. Sometimes required
	since RTBox puts the 0-bit on pin 8 but receiving device may put
	it on pin 1, like Brain Products actiCHamp).

	Pin assignments on RTBox are also shifted by one relative to
	most receiving ports, so we do that too.

	Input is just an int 
	'''
	bin_str = bin(n)[2:]
	k = len(bin_str)
	if k <= 7: # zero pad up to 8 bits
		bin_str = (8 - k) * '0' + bin_str
	else:
		raise ValueError(
			"Brain Products only takes 7-bit ints (0<n<128)" + 
			" from RTBox (since pin assignments aren't aligned)."
			)
	return int(bin_str[::-1], 2) >> 1 # reverse and shift by one


class EventMarker:
	'''
	Small helper for sending 8-bit integer event codes with RTBox

	Pretty much only useful for the bit reversal functionality, otherwise
	the RTBox API is just as easy.
	'''

	def __init__(self, reverse_bits = True):
		'''
		reverse_bits (bool): whether to reverse the 8-bit event code,
		as is necessary for Brainvision Triggerbox to read correctly
		over parallel port (since pin assignments are opposite of RTBox).
		'''
		self._revbits = reverse_bits
		self.box = Box()

	def send(self, event_code):
		'''
		Sends 8-bit event code and returns timestamp w/ upper bound
		'''
		assert(type(event_code) is int)
		if self._revbits:
			event_code = revbits(event_code)
		send_time, upper_bound = self.box.TTL(event_code)
		return send_time, upper_bound

	def close(self):
		'''
		Call this before ending script or RTBox will be sad
		(you'll get a serial port conflict down the line)
		'''
		self.box.close()




