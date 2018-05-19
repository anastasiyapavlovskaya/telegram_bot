import logging
import telegram
import pickle as pkl
from telegram.error import NetworkError, Unauthorized
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler

with open('model.pkl', 'rb') as input_file:
    model = pkl.load(input_file)
with open('vectorizer.pkl', 'rb') as input_file:
    vc = pkl.load(input_file)

classification = {0: 'Credit reporting', 
                  1: 'Consumer Loan',
                  2: 'Debt collection',
                  3: 'Mortgage',
                  4: 'Credit card',
                  5: 'Other financial service',
                  6: 'Bank account or service',
                  7: 'Student loan',
                  8: 'Money transfers',
                  9: 'Payday loan',
                  10: 'Prepaid card',
                  11: 'Money transfer',
                  12: 'Personal consumer reports',
                  13: 'Checking or savings account',
                  14: 'Vehicle loan or lease',
                  15: 'Credit card or prepaid card',
                  16: 'Virtual currency',
                  17: 'All kindes of loans'}

def start(bot, update):
    button_list = [telegram.InlineKeyboardButton("Complain", callback_data='complain'),
                   telegram.InlineKeyboardButton("Visit WebSite", 
                                                 url='https://catalog.data.gov/dataset/consumer-complaint-database', 
                                                 callback_data='Web')]
    reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    bot.send_message(chat_id=update.message.chat_id, text="Welcome to Client Support System.\n Just write your complaint and we will deal with it as soon as possible.",
                     reply_markup=reply_markup)

def help_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Help menu:\n /start - start to chat with bot\n /exit - stop to chat with bot\n\n Follow the instructions of the bot.")

    
def exit(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Goodbye! Hope hearing from your soon!")
    
def parse_callback(bot, update):
    try:
        if update.callback_query['data'] == 'complain':
            bot.send_message(update.callback_query.message['chat']['id'], text='We are sorry you do not like our service. Simply wright your complaint.')
        
        elif update.callback_query['data'] == 'yes':
            with open('all_complaints.txt', 'a') as output_file:
                output_file.write(' yes')
                output_file.write('\n')
            bot.send_message(update.callback_query.message['chat']['id'], text='Great! We will deal with it!\nThank you for your complaint.')
            button_list = [telegram.InlineKeyboardButton("Complain", callback_data='complain'),
                           telegram.InlineKeyboardButton("Everithing is alright and you are awesome", callback_data='awesome'),
                           telegram.InlineKeyboardButton("Visit website", 
                                                         url='https://catalog.data.gov/dataset/consumer-complaint-database',)]
            reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    
            bot.send_message(update.callback_query.message['chat']['id'], 
                             text='Would you like to write something else? Your opinion is important.',
                             reply_markup=reply_markup)
            
        
        elif update.callback_query['data'] == 'no':
            with open('all_complaints.txt', 'a') as output_file:
                output_file.write(' no')
                output_file.write('\n')
            bot.send_message(update.callback_query.message['chat']['id'], text='Hm, could you write in another words this problem?')
        
        elif update.callback_query['data'] == 'awesome':
            bot.send_message(update.callback_query.message['chat']['id'], text='Thank you! You are awesome too:3')
    
    except BaseException as e:
        print('exception', e)
            
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def process_update(bot, update, update_queue):
    #if update.message or update.inline_message_id:
    for i in range(3):
        try:
            if update.message:
                message = update.message
            else:
                message = update.callback_query.message
            chat_id = message.chat_id
            user = update.effective_user
            button_list = [telegram.InlineKeyboardButton("Another complaint", callback_data='next')]

            if message.text == 'хочу комплимент!':
                reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
                bot.send_message(message.chat_id, 'You are so beautiful!!')
                for photo in user.get_profile_photos()['photos']:
                    bot.send_photo(message.chat_id, photo=photo[0].file_id, callback_data='photo')
            
            else:
                button_list = [telegram.InlineKeyboardButton("Yes", callback_data='yes'),
                               telegram.InlineKeyboardButton("No", callback_data='no')]
                pred = model.predict(vc.transform([message.text]))

                with open('all_complaints.txt', 'a') as output_file:
                    output_file.write('{} {}'.format(message.text, pred[0]))

                reply_markup = reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
                bot.send_message(message.chat_id, text='Seems that you are complaining about {}. Am I right?'.format(classification[pred[0]]),
                                 reply_markup=reply_markup)
            break
        
        except BaseException as e:
            print('exception', e, ', retrying')
            continue
            
def main():
    """Run the bot."""
    # Telegram Bot Authorization Token
    print('Starting bot')
    token = '...'
    updater = Updater(token, request_kwargs={'proxy_url':'socks5://97.74.230.16:6842/'})

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('exit', exit))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CallbackQueryHandler(parse_callback))
    dispatcher.add_handler(MessageHandler(Filters.text, process_update, pass_update_queue=True))
    
    bot = updater.bot
    
    print('Connected to the server!')
    updater.start_polling()
    updater.idle()
        
main()