
class Knowledge:
	def __init__(self, named="", topicsd="", descriptiond="", modeld="", arquivod="", attributes="none", dependencesp = "none", typep = "passive"):
		self.name = named
		self.topics = topicsd
		self.description= descriptiond
		self.model=modeld
		self.arquivo=arquivod
		self.att = attributes
		self.dependences= dependencesp
		self.type = typep

	def tostring (self):
		atributos = ""
		for i in self.attributes:
			atributos = atributos + " " + i
		return "========\n" + str (self.name)+ "\n"  + str (self.description) + "\nArgs:" + str (atributos)
