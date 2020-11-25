import ui
from datetime import datetime
import requests, json

#################################
# Views
#################################

screen_width = ui.get_screen_size().width

# DatePicker
dp_rep_date = ui.DatePicker()
dp_rep_date.mode = 1
dp_rep_date.x = 0
dp_rep_date.y = 0
dp_rep_date.width = screen_width
dp_rep_date.height = 100
dp_rep_date.date = datetime.today()
dp_rep_date.border_width = 1

# Label: Amount from
lb_amnt_from = ui.Label()
lb_amnt_from.text = 'Amount from:   '
lb_amnt_from.x = 0
lb_amnt_from.y = 101
lb_amnt_from.height = 35
lb_amnt_from.width = screen_width / 2
lb_amnt_from.alignment = 1
lb_amnt_from.border_width = 1

# TextField: Amount from
tf_amnt_from = ui.TextField()
tf_amnt_from.x = screen_width / 2
tf_amnt_from.y = 101
tf_amnt_from.width = screen_width / 2
tf_amnt_from.height = 35
tf_amnt_from.keyboard_type = ui.KEYBOARD_NUMBERS
tf_amnt_from.border_width = 1

# Label: Currency from
lb_cur_from = ui.Label()
lb_cur_from.border_width = 1
lb_cur_from.text = 'Currency from'
lb_cur_from.x = 0
lb_cur_from.y = 137
lb_cur_from.height = 35
lb_cur_from.width = screen_width / 2
lb_cur_from.alignment = 1

# Label: Currency to
lb_cur_to = ui.Label()
lb_cur_to.border_width = 1
lb_cur_to.text = 'Currency to'
lb_cur_to.x = screen_width / 2
lb_cur_to.y = 137
lb_cur_to.height = 35
lb_cur_to.width = screen_width / 2
lb_cur_to.alignment = 1

# TableView: Currency from
tv_cur_from = ui.TableView()
tv_cur_from.border_width = 1
tv_cur_from.x = 0
tv_cur_from.y = 173
tv_cur_from.width = screen_width / 2
tv_cur_from.height = 200


# TableView: Currency from
tv_cur_to = ui.TableView()
tv_cur_to.border_width = 1
tv_cur_to.x = screen_width / 2
tv_cur_to.y = 173
tv_cur_to.width = screen_width / 2
tv_cur_to.height = 200

# Button: convert
bt_convert = ui.Button()
bt_convert.border_width = 4
bt_convert.title = 'Convert'
bt_convert.x = 0
bt_convert.y = 380
bt_convert.width = screen_width
bt_convert.height = 50
bt_convert.font = ('verdana',25)
bt_convert.corner_radius = 20

# TextView: amount about conversion
txtv_info = ui.TextView()
txtv_info.x = 0
txtv_info.y = 440
txtv_info.width = screen_width
txtv_info.height = 150
txtv_info.editable = False
txtv_info.font = ('verdana', 18)
txtv_info.border_width = 1

#################################
# Global class
#################################

class MyClass(ui.View):

	date         = ''
	amnt_from    = ''
	amnt_to      = ''
	cur_from     = ''
	cur_to       = ''
	xchange_to   = ''
	xchange_from = ''
	
	currency_list = ['BYN','USD','EUR','RUB','GBP','UAH','PLN']
	
	data_src_cur_from = ui.ListDataSource(currency_list)
	
	data_src_cur_to = ui.ListDataSource(currency_list)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.table1_selection = None
		self.bg_color = 'lightyellow'
		self.make_view()
		
	def make_view(self):
		self.add_subview(dp_rep_date)
		self.add_subview(lb_amnt_from)
		self.add_subview(tf_amnt_from)
		self.add_subview(lb_cur_from)
		self.add_subview(lb_cur_to)
		self.add_subview(tv_cur_from)
		self.add_subview(tv_cur_to)
		self.add_subview(bt_convert)
		self.add_subview(txtv_info)
		
		# Actions
		dp_rep_date.action = self.fn_date_selected
		
		tf_amnt_from.action = self.fn_amnt_entered
		
		self.data_src_cur_from.action = self.fn_cur_from_selected
		
		tv_cur_from.data_source = tv_cur_from.delegate = self.data_src_cur_from
		
		self.data_src_cur_to.action = self.fn_cur_to_selected
		
		tv_cur_to.data_source = tv_cur_to.delegate = self.data_src_cur_to
		
		bt_convert.action = self.fn_convert
		
		
	def fn_date_selected(self, sender):
		self.date = sender.date
		
	def fn_amnt_entered(self, sender):
		self.amnt_from = sender.text
		
	def fn_cur_from_selected(self, sender):
		self.cur_from = sender.items[sender.selected_row]
		
	def fn_cur_to_selected(self, sender):
		self.cur_to = sender.items[sender.selected_row]
		
	def fn_convert(self, sender):
	
		# Формируем дату
		if self.date == '':
			self.date = datetime.today()
			
		rep_date = datetime.strftime(self.date, '%Y-%m-%d')
		
		# Достаем все курс валюты на дату
		response = requests.get(f'https://www.nbrb.by/api/exrates/rates?ondate={ rep_date }&periodicity=0')
		cur_list = json.loads(response.content)
		
		if self.cur_from != 'BYN':
			cur_from_info = list(filter(lambda person: person['Cur_Abbreviation'] == self.cur_from , cur_list))
		else:
			cur_from_info = [{ 'Cur_Abbreviation': 'BYN', 'Cur_Scale': 1, 'Cur_OfficialRate': 1 }]
			
		if self.cur_to != 'BYN':
			cur_to_info = list(filter(lambda person: person['Cur_Abbreviation'] == self.cur_to , cur_list))
		else:
			cur_to_info = [{ 'Cur_Abbreviation': 'BYN', 'Cur_Scale': 1, 'Cur_OfficialRate': 1 }]
			
		# Расчёт суммы:
		# Целевая сумма = исходная сумма * ( курс исх. валюты * коэф. целевой валюты ) / (курс цел. валюты * коэф. исх. валюты).
		
		self.amnt_to = float(self.amnt_from) * (float(cur_from_info[0]['Cur_OfficialRate']) * int(cur_to_info[0]['Cur_Scale'])) / (float(cur_to_info[0]['Cur_OfficialRate']) * int(cur_from_info[0]['Cur_Scale']) )
		
		txtv_info.text = f'{ self.amnt_from} { self.cur_from} = { round(self.amnt_to,2)} {self.cur_to}'
		
		
##################
# Зауск
##################
v = MyClass(name='Currency converter')
v.present('full_screen')
