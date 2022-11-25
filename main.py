import tkinter as tk
from tkinter import ttk
from gl2f.core import lister, terminal as term, date
from gl2f.core.board import content_url
import webbrowser
import pyperclip


def selected(tree, items):
	for i in tree.selection():
		yield items[int(i)]

def create_copy_url(tree, items):
	def f():
		text = ' '.join(map(content_url, selected(tree, items)))
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
			lambda i: i['values']['title'] + ' ' + content_url(i),
			selected(tree, items)
		))
		print('copying text', text, flush)
		pyperclip.copy(text)
	return f

def create_open(tree, items):
	def f():
		for i in selected(tree, items):
			url = content_url(i)
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
			'format':content_url,
			'width':300,
		},
		'date': {
			'format':lambda i:date.to_datetime(i['openingAt']).strftime('%m/%d %H:%M:%S'),
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
			values=[term.declip(colspec[k]['format'](item)) for k in cols])


	add_menu(tree, items)

	scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	tree.configure(yscroll=scrollbar.set)

	frame.pack(fill=tk.X, padx=16, pady=(4,16))
	tree.pack(fill=tk.X)
	scrollbar.pack()

	return frame


class App:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title('GL2F familiar tabulator')
		# self.root.geometry('800x300')

		self.run = self.root.mainloop

		self.create_header()


		self.columns = 'date', 'category', 'title'
		self.fetch()


	def create_header(self):
		self.header = ttk.Frame(self.root)
		self.header.pack(fill = tk.BOTH, padx=16, pady=(8, 2))

		self.board = ttk.Combobox(self.header, state='readonly', values=[
			'today',
			'blogs/girls2',
			'blogs/lucky2',
			'radio/girls2',
			'radio/lucky2',
			'news/family',
			'news/girls2',
			'news/lucky2',
			'gtube',
		])

		self.board.current(0)
		self.board.bind('<<ComboboxSelected>>', self.fetch)
		self.board.pack(side=tk.LEFT)


	def fetch(self, *_):

		class args:
			board = self.board.get()
			number=20
			page=1
			order='reservedAt:desc'
			dump = False

		self.items = lister.listers(args)
		self.update_table()


	def update_table(self):
		try:
			self.table.destroy()
		except:
			pass

		self.table = create_table(self.root, self.columns, self.items)


if __name__ == '__main__':
	app = App()
	app.run()
