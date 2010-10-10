# -*- coding: iso-8859-1 -*-
from Components.Language import language
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap

class VirtualKeyBoardList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 22))
		self.l.setItemHeight(45)

def VirtualKeyBoardEntryComponent(keys, selectedKey,shiftMode=False):
	key_backspace = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_backspace.png"))
	key_bg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_bg.png"))
	key_clr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_clr.png"))
	key_esc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_esc.png"))
	key_ok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_ok.png"))
	key_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_sel.png"))
	key_shift = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_shift.png"))
	key_shift_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_shift_sel.png"))
	key_space = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/vkey_space.png"))
	
	res = [ (keys) ]
	
	x = 0
	count = 0
	if shiftMode:
		shiftkey_png = key_shift_sel
	else:
		shiftkey_png = key_shift
	for key in keys:
		if key == "EXIT":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_esc))
		elif key == "BACKSPACE":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_backspace))
		elif key == "CLEAR":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_clr))
		elif key == "SHIFT":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=shiftkey_png))
		elif key == "SPACE":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_space))
		elif key == "OK":
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_ok))
		#elif key == "<-":
		#	res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_left))
		#elif key == "->":
		#	res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_right))
		
		else:
			res.extend((
				MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_bg),
				MultiContentEntryText(pos=(x, 0), size=(45, 45), font=0, text=key.encode("utf-8"), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER)
			))
		
		if selectedKey == count:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_sel))
		
		x += 45
		count += 1
	
	return res


class VirtualKeyBoard(Screen):

	def __init__(self, session, title="", text=""):
		Screen.__init__(self, session)
		self.keys_list = []
		self.shiftkeys_list = []
		self.lang = language.getLanguage()
		if self.lang == 'de_DE':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"�", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"�", u"�", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"�", u"OK"]]
			
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"�", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"�", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"�", u"�", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"OK"]]
			
		elif self.lang == 'es_ES':
			#still missing keys (u"��")
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"�", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"�", u"�", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"�", u"�", u"�", u"�", u"�", u"�", u"�", u"�", u"OK"]]
			
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"�", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"�", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"�", u"�", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"�", u"�", u"�",  u"�", u"�", u"�", u"�", u"OK"]]
				
		elif self.lang in ('sv_SE', 'fi_FI'):
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"�", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"�", u"�", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"�", u"�", u"OK"]]
				
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"�", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"�", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"�", u"�", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],

				[u"SHIFT", u"SPACE", u"?", u"\\", u"�", u"OK"]]
		else:
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"OK"]]
			
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"�", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"OK"]]
		
		self.shiftMode = False
		self.text = text
		self.selectedKey = 0
		
		self["header"] = Label(title)
		self["text"] = Label(self.text)
		self["list"] = VirtualKeyBoardList([])
		
		self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions"],
			{
				"ok": self.okClicked,
				"cancel": self.exit,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
				"red": self.backClicked,
				"green": self.ok
			}, -2)
		
		self.onLayoutFinish.append(self.buildVirtualKeyBoard)
	
		self.max_key=47+len(self.keys_list[4])

	def buildVirtualKeyBoard(self, selectedKey=0):
		list = []
		
		if self.shiftMode:
			self.k_list = self.shiftkeys_list
			for keys in self.k_list:
				if selectedKey < 12 and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey,True))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1,True))
				selectedKey -= 12
		else:
			self.k_list = self.keys_list
			for keys in self.k_list:
				if selectedKey < 12 and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1))
				selectedKey -= 12
		
		self["list"].setList(list)

	
	def backClicked(self):
		self.text = self["text"].getText()[:-1]
		self["text"].setText(self.text)
			
	def okClicked(self):
		if self.shiftMode:
			list = self.shiftkeys_list
		else:
			list = self.keys_list
		
		selectedKey = self.selectedKey

		for x in list:
			if selectedKey < 12:
				text = x[selectedKey]
				break
			else:
				selectedKey -= 12

		text = text.encode("utf-8")

		if text == "EXIT":
			self.close(None)
		
		elif text == "BACKSPACE":
			self.text = self["text"].getText()[:-1]
			self["text"].setText(self.text)
		
		elif text == "CLEAR":
			self.text = ""
			self["text"].setText(self.text)
		
		elif text == "SHIFT":
			if self.shiftMode:
				self.shiftMode = False
			else:
				self.shiftMode = True
			
			self.buildVirtualKeyBoard(self.selectedKey)
		
		elif text == "SPACE":
			self.text += " "
			self["text"].setText(self.text)
		
		elif text == "OK":
			self.close(self["text"].getText())
		
		else:
			self.text = self["text"].getText()
			self.text += text
			self["text"].setText(self.text)

	def ok(self):
		self.close(self["text"].getText())

	def exit(self):
		self.close(None)

	def left(self):
		self.selectedKey -= 1
		
		if self.selectedKey == -1:
			self.selectedKey = 11
		elif self.selectedKey == 11:
			self.selectedKey = 23
		elif self.selectedKey == 23:
			self.selectedKey = 35
		elif self.selectedKey == 35:
			self.selectedKey = 47
		elif self.selectedKey == 47:
			self.selectedKey = self.max_key
		
		self.showActiveKey()

	def right(self):
		self.selectedKey += 1
		
		if self.selectedKey == 12:
			self.selectedKey = 0
		elif self.selectedKey == 24:
			self.selectedKey = 12
		elif self.selectedKey == 36:
			self.selectedKey = 24
		elif self.selectedKey == 48:
			self.selectedKey = 36
		elif self.selectedKey > self.max_key:
			self.selectedKey = 48
		
		self.showActiveKey()

	def up(self):
		self.selectedKey -= 12
		
		if (self.selectedKey < 0) and (self.selectedKey > (self.max_key-60)):
			self.selectedKey += 48
		elif self.selectedKey < 0:
			self.selectedKey += 60	
		
		self.showActiveKey()

	def down(self):
		self.selectedKey += 12
		
		if (self.selectedKey > self.max_key) and (self.selectedKey > 59):
			self.selectedKey -= 60
		elif self.selectedKey > self.max_key:
			self.selectedKey -= 48
		
		self.showActiveKey()

	def showActiveKey(self):
		self.buildVirtualKeyBoard(self.selectedKey)
