from config import files


class File():
	def __init__(self, name):
		self.address = 'response/' + name
		self.text = ''
		
		self.info = {}


	def reading(self):
		self.file = open(self.address, 'r+')
		self.text = self.file.read().split(';')
		if len(self.text) > 0 and len(self.text[0]) > 0:
			for z in self.text:
				i, j = z.split(': ')
				self.info[i] = int(j)
		self.file.close()


	def printing(self):
		return self.info


	def information(self):
		print(f'<link=\'{self.address}\', mode=\'r+\', encoding=\'cp1252\'')
		print(self.info)


	def writing(self, positions):
		print(positions)
		self.file = open(self.address, 'w')
		text = []
		for ids in positions:
			text.append(f'{ids}: {positions[ids]}')
		self.file.write(';'.join(text))
		self.file.close()
