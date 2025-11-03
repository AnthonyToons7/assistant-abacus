from handlers.ProgramHandler import open_program, message_checklist

def filter(text):
    text = text.lower()
    activation_commands = ['send', 'open', 'fetch', 'settings']
    # availablePlatforms = ['discord', 'whatsapp', 'spotify']

    # TODO: make arrays with apps based off of what the commands are. for example:
    # activation_commands = 'send'
    # availableApps = ['discord', 'whatsapp', 'telegram']
    # Try to filter through what purpose is what app. Furthermore, add additional filters for misspeaking just like 'aba cus', 'avacus'

    # TODO: cut sentences into words and filter cout activation commands and applications / messages to send
    # If a activation command is met, but no application, restart the listening sequence, and ask for an application
    #  If the application is met, and the command is 'send', but no message has been added, restart listening sequence
    # After listening sequence save the sentence, and read it out with TTS

    text = text.split(' ')
    application = ''
    activation_word = ''

    for i, word in enumerate(text):
        if word in activation_commands:
            activation_word = text[i]

            if activation_word == 'open':
                if i + 1 < len(text):
                    application = text[i + 1]
                break

        if activation_word == 'send' and word == 'on':
            if i + 1 < len(text):
                application = text[i + 1]
            break

    match activation_word:
        case 'send':
            message_checklist(application)
        case 'open':
            open_program(application)
        case _:
            return 'Empty'
            
    return 'Success!'
