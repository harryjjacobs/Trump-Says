"""
Harry Jacobs 2017
Program to output ASCII art of Donald Trump saying stuff.
Can also be imported as a module.

Usage:

Can be run without command line arguments in which case it will select
a random quote from the quotes.txt file or a random recent tweet from his
twitter timeline.

Otherwise specify what he says by providing an argument: trump_says.py "Hello world"

"""

import sys
import re
import random
import time
import uuid
import json
import base64
import string

# For python 2 and 3 compat
try:
	from urllib.request import urlopen, Request
except ImportError:
	from urllib2 import urlopen, Request


class TweetFetcher():
	"""
	A class for accessing the twitter api to fetch recent tweets for a
	given user.
	"""
	BASE_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
	QUERY_STRING = '?screen_name={handle}'
	CONSUMER_KEY = 'pZaFxGSR8yc9CC2GkZ9iGBRVY'
	CONSUMER_SECRET = 'sil6xmNLB3AWxq6PnVek8PX2FNImkHtqyyPxJLFlUOXRE7DqwG'
	OAUTH_TOKEN_URL = 'https://api.twitter.com/oauth2/token'

	def __init__(self):
		self.bearer_token = self.fetch_bearer_token()
		
	def fetch(self, handle):
		"""
		Returns a list containing tweets in dictionary form.
		"""
		req = self.build_request(handle)
		resp = urlopen(req)
		if resp.code == 200:
			content = resp.read()
			return json.loads(content)

	def build_request(self, handle):
		if self.bearer_token:
			req = Request((TweetFetcher.BASE_URL+TweetFetcher.QUERY_STRING).format(handle=handle))
			req.add_header('Authorization', 'Bearer {0}'.format(self.bearer_token))
			return req
		else:
			self.bearer_token = self.fetch_bearer_token()
			return self.build_request()

	def fetch_bearer_token(self):
		req = Request(TweetFetcher.OAUTH_TOKEN_URL, 'grant_type=client_credentials')
		auth_header = self.generate_bearer_token_credentials()
		req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
		req.add_header('Authorization', 'Basic {0}'.format(auth_header))
		resp = urlopen(req)
		if resp.code == 200:
			content = resp.read()
			token = json.loads(content)['access_token']
			return token
		else:
			print("Error fetching bearer token")

	def generate_bearer_token_credentials(self):
		token = '{0}:{1}'.format(TweetFetcher.CONSUMER_KEY,
								 TweetFetcher.CONSUMER_SECRET)
		return base64.b64encode(token)

	@classmethod
	def timestamp(cls):
		return int(time.time())

	@classmethod
	def generate_nonce(cls):
		return uuid.uuid4().hex


class ASCIITrump():
	"""
	A class for printing an ASCII Donald Trump with a speech bubble
	"""
	LINES_RE = re.compile("(\$)")

	def __init__(self, quiet=False):
		self.quiet = quiet

		self.max_line_width = 43
		self.line_count = 4
		self.ascii = '''
	                 ___________________________________________
	                /                                           \\
	   ,------._    | $|
	  /         :   | $|
	 /  ,-__-.  :   | $|
	; ,' _   _`-|  /  $|
	|/  - ||-   | / _____________________________________________/
	|\   /_\    |---
	:|         |;
	\     o    ;
	 \         ;
	  `--+---'
		'''

	def say(self, message):
		"""
		Fill in the ASCII art speech bubble with the message and print
		the result.
		"""
		if len(message) > self.max_line_width * self.line_count:
			self.log('Error, message too long')
			return False

		# set up lines list to store the lines in. Pad all lines
		# with spaces apart from the first in case they don't get used.
		lines = [' ' * (self.max_line_width)] * (self.line_count-1)
		lines.insert(0, '')

		words = message.split(' ')
		i = 0 # line index
		for word in words:
			if len(lines[i] + word) + 1 <= self.max_line_width:
				# add a word to the current line
				lines[i] += word + ' '

			elif len(word) < self.max_line_width and i + 1 < len(lines):
				# pad the previous line to reform the speech bubble
				lines[i] += ' ' * (self.max_line_width - len(lines[i]))
				# start a new line as we've reached the end of the previous one
				i += 1
				lines[i] = word + ' '

			elif len(word) > self.max_line_width:
				# the word is too big for our speech bubble ( > max_line_width)
				self.log("Error - Trump doesn't know any words as long as that")
				return False

			elif len(lines[i] + word) + 1 > self.max_line_width:
				self.log('Error, message too long' + word)
				return False

		# pad the last line
		lines[i] += ' ' * (self.max_line_width - len(lines[i]))

		# substitute each of the doller signs in the ascii with our lines
		# and return the result
		result = ASCIITrump.LINES_RE.sub(lambda x: lines.pop(0), self.ascii)

		# print output
		print(result)
		return True

	def log(self, message):
		if not self.quiet:
			print(message)


def fetch_tweets():
	fetcher = TweetFetcher()
	return fetcher.fetch('realDonaldTrump')

def remove_invalid_chars(text):
	return ''.join(x for x in text if x in string.printable and x != '\n')

def main():
	"""
	Open the quotes.txt file. Each quote should be separated by a newline.
	Chooses a random quote and gets ASCII Trump to say it.
	"""
	quotes = []
	with open('quotes.txt', 'r') as file:
		quotes = file.read().split('\n')

	# grab tweets and add to quotes list
	tweets = fetch_tweets()
	if (tweets):
		for tweet in tweets:
			text = remove_invalid_chars(tweet['text'])
			quotes.append(text)

	trump = ASCIITrump(quiet=True)
	success = trump.say(random.choice(quotes))
	while not success:
		success = trump.say(random.choice(quotes))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		trump = ASCIITrump()
		success = trump.say(sys.argv[1])
	else:
		main()