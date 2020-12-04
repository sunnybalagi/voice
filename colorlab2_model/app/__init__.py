from flask import Flask

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'0#&%)*!%Y(*G!U%BUJb98ho1j5khbLKUTGBlkeaklutgalkuegtlkug'

from app import routes
