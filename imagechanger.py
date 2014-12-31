import os
import flask
from flask import Flask, render_template, send_file, request
from werkzeug import secure_filename
from PIL import Image

ON_OPENSHIFT = os.environ.get('OPENSHIFT_REPO_DIR', False)
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])

app = Flask(__name__, static_folder = 'wsgi/static')
app.config['APP_PATH'] = os.path.dirname(os.path.abspath(__file__))

if ON_OPENSHIFT:
	app.debug = False
	app.config['TEMP_DIR'] = os.environ['OPENSHIFT_TMP_DIR']
else:
	app.debug = True
	app.config['TEMP_DIR'] = '/tmp'


@app.route('/', methods = ['GET', 'POST'])
def main_page():
	if request.method == 'POST':
		filename = os.path.join(app.config['TEMP_DIR'], secure_filename(request.files['file'].filename))
		request.files['file'].save(filename)
		newname, e = os.path.splitext(filename)
		newname = newname + '.' + request.form['format']
		if newname != filename:
			try:
				Image.open(filename).save(newname)
			except IOError as e:
				print 'Could not convert'
				print e.strerror
				return '<h1>Error converting</h1>'
		@flask.after_this_request
		def cleanup_files(response):
			os.remove(filename)
			os.remove(newname)
			return response
		return send_file(newname, as_attachment = True)
	
	return render_template('main_page.html')





if __name__ == '__main__':
	app.run()
