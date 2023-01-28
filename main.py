import tkinter as tk
from tkinter import ttk
import gl2f
from gl2f.core import util
import webbrowser
import pyperclip
from datetime import datetime

class const:
	pages = gl2f.board.tree()
	groups = ['girls2', 'lucky2', 'lovely2']
	members = {g: list(gl2f.member.of_group(g).keys()) for g in groups}
	page_order = ['today'] + list(dict.fromkeys(i.split('/')[0] for i in gl2f.board.active()))


def selected(tree, items):
	for i in tree.selection():
		yield items[int(i)]

def create_copy_url(tree, items):
	def f():
		text = ' '.join(map(gl2f.content_url, selected(tree, items)))
		print('copying text', text, flush=True)
		pyperclip.copy(text)
	return f

def create_copy_title(tree, items):
	def f():
		text = ' '.join(map(
			lambda i: i['values']['title'],
			selected(tree, items)
		))
		print('copying text', text, flush=True)
		pyperclip.copy(text)
	return f

def create_copy_titleurl(tree, items):
	def f():
		text = ' '.join(map(
			lambda i: i['values']['title'] + ' ' + gl2f.content_url(i),
			selected(tree, items)
		))
		print('copying text', text, flush=True)
		pyperclip.copy(text)
	return f

def create_open(tree, items):
	def f():
		for i in selected(tree, items):
			url = gl2f.content_url(i)
			print('opening', url, flush=True)
			webbrowser.open(url, new=0, autoraise=True)
	return f


def add_menu(tree, items):
	create = {
		'open': create_open,
		'copy url': create_copy_url,
		'copy title': create_copy_title,
		'copy title + url': create_copy_titleurl,
	}

	menu = tk.Menu(tree, tearoff=0)

	for k, v in create.items():
		menu.add_command(label=k, command=v(tree,items))

	tree.bind('<Button-3>', lambda e:menu.post(e.x_root, e.y_root))
	tree.bind('<Button-2>', lambda e:menu.post(e.x_root, e.y_root))


def create_table(root, cols, items):
	colspec = {
		'category': {
			'format': lambda i:i.get('category', {'name':''})['name'],
			'width':80,
		},
		'title': {
			'format':lambda i:i['values']['title'],
			'width':600,
		},
		'url': {
			'format':gl2f.content_url,
			'width':300,
		},
		'date': {
			'format':lambda i:util.to_datetime(i['openingAt']).strftime('%m/%d %H:%M:%S'),
			'width':40
		},
	}

	frame = ttk.Frame(root)
	tree = ttk.Treeview(frame, columns=cols)

	tree.column('#0', stretch='no', width=0)
	for k in cols:
		tree.column(k, width=colspec[k]['width'])

	tree.heading('#0',text='')
	for k in cols:
		tree.heading(k, text=k)

	for index, item in enumerate(items):
		tree.insert(parent='', index='end', iid=index,
			values=[colspec[k]['format'](item) for k in cols])


	add_menu(tree, items)

	scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	tree.configure(yscroll=scrollbar.set)

	frame.pack(fill=tk.X, padx=16, pady=(4,16))
	tree.pack(fill=tk.X)
	scrollbar.pack()

	return frame


def create_root():
	root = tk.Tk()
	root.title('GL2 familiar tabulator')
	# root.geometry('800x300')
	root.bind('<Control-w>', lambda _:root.destroy())

	return root


class App:
	def __init__(self):
		self.root = create_root()

		self.create_header()

		self.columns = 'date', 'category', 'title'
		self.fetch()


	def create_header(self):
		self.header = ttk.Frame(self.root)
		self.header.pack(fill = tk.BOTH, padx=16, pady=(8, 2))


		keys = list(const.pages.keys())
		keys.sort()
		keys.sort(key=lambda x: const.page_order.index(x) if x in const.page_order else 1000)


		self.button = tk.Button(self.header, text='reload', command=self.fetch)
		self.button.pack(side=tk.LEFT)


		self.board_first = ttk.Combobox(self.header, state='readonly', values=keys)

		self.board_first.current(0)
		self.board_first.bind('<<ComboboxSelected>>', self.create_board_second)
		self.board_first.pack(side=tk.LEFT, padx=(4, 0))

		self.board_second = None

		self.timestring = tk.StringVar()
		self.timelabel = tk.Label(self.header, textvariable=self.timestring)
		self.timelabel.pack(side=tk.RIGHT)


	def create_board_second(self, *_):
		try:
			self.board_second.destroy()
			self.board_second = None
		except:
			pass


		order = ['today', 'family'] + const.groups + sum((const.members[g] for g in const.groups), [])

		second = list(const.pages[self.board_first.get()])
		second.sort()
		second.sort(key=lambda x: order.index(x) if x in order else 1000)

		if len(second)>0:
			self.board_second = ttk.Combobox(self.header, state='readonly', values=second)
			self.board_second.current(0)
			self.board_second.bind('<<ComboboxSelected>>', self.fetch)
			self.board_second.pack(side=tk.LEFT, padx=(4,0))

		else:
			self.fetch()


	def fetch(self, *_):
		class args:
			board = self.board_first.get() + (f'/{self.board_second.get()}' if self.board_second else '')
			number=20
			page=1
			order='reservedAt:desc'
			dump = False
			group=None

		self.items = gl2f.list_contents(args)
		self.update_table()

		self.timestring.set(datetime.now().strftime('seen at %H:%M'))


	def update_table(self):
		try:
			self.table.destroy()
		except:
			pass

		self.table = create_table(self.root, self.columns, self.items)


if __name__ == '__main__':
	import sys

	app = App()
	if 'noloop' not in sys.argv:
		app.root.mainloop()
