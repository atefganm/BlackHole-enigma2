from enigma import eListboxPythonStringContent, eListbox
from Components.GUIComponent import GUIComponent


class MenuList(GUIComponent):
	def __init__(self, list, enableWrapAround=True, content=eListboxPythonStringContent):
		GUIComponent.__init__(self)
		self.l = content()  # noqa: E741
		self.onSelectionChanged = []
		self.setList(list)
		self.enableWrapAround = enableWrapAround

	def enableAutoNavigation(self, enabled):
		if self.instance:
			self.instance.enableAutoNavigation(enabled)

	def getCurrent(self):
		return self.l.getCurrentSelection()

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		instance.selectionChanged.get().append(self.selectionChanged)
		if self.enableWrapAround:
			self.instance.setWrapAround(True)

	def preWidgetRemove(self, instance):
		instance.setContent(None)
		instance.selectionChanged.get().remove(self.selectionChanged)

	def selectionChanged(self):
		for f in self.onSelectionChanged:
			f()

	def getSelectionIndex(self):
		return self.l.getCurrentSelectionIndex()

	def getSelectedIndex(self):
		return self.l.getCurrentSelectionIndex()

	def setList(self, list):
		self.list = list
		self.l.setList(self.list)
		self.selectionChanged()

	def moveToIndex(self, idx):
		if self.instance is not None:
			self.instance.moveSelectionTo(idx)

	def moveTop(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveTop)

	def moveBottom(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveEnd)

	def pageUp(self):
		print("menulist pageUp")
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageUp)

	def pageDown(self):
		print("menulist pageDown")
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageDown)

	# Add new moveUp method for symmetry with ConfigList
	def moveUp(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveUp)

	# Add new moveDown method for symmetry with ConfigList
	def moveDown(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveDown)

	# Maintain the old up method for legacy compatibility
	def up(self):
		self.moveUp()

	# Maintain the old down method for legacy compatibility
	def down(self):
		self.moveDown()

	def selectionEnabled(self, enabled):
		if self.instance is not None:
			self.instance.setSelectionEnable(enabled)
