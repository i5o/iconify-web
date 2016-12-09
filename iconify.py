#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Ignacio Rodríguez <ignacio@sugarlabs.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename
import os
import uuid
from sugariconify import SugarIconify
from xocolor import random_color

app = Flask(__name__)
script_path = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(script_path, "static/")
wip_path = os.path.join(static_path, "wip/")
done_path = os.path.join(static_path, "done/")
random_path = os.path.join(static_path, "random/")

finder = re.compile(
    ur"\t<!ENTITY stroke_color \"([\S*]+)\">\n\t<!ENTITY fill_color \"([\S*]+)\">")
stroke_color = '<!ENTITY stroke_color "{color}">'
fill_color = '<!ENTITY fill_color "{color}">'


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect("/?error=yup")

        file = request.files['file']
        if file.filename == '':
            return redirect("/?error=yup")

        if file and file.filename[-4:] == ".svg":
            filename = file.filename
            filename = str(uuid.uuid4()) + "_" + filename
            filename = secure_filename(filename)
            file.save(os.path.join(wip_path, filename))
            return redirect(url_for('index', filename=filename))

    return redirect("/?error=yup")

@app.route('/', methods=['GET'])
def index():
    file_name = request.args.get('filename')
    error = request.args.get('error')
    original_file = None
    sugarized_file = None

    if file_name:
        original_file = os.path.join(wip_path, file_name)
        sugarized_file = os.path.join(done_path, file_name)

        try:
            iconify = SugarIconify()
            iconify.iconify(original_file, sugarized_file)
        except:
            return redirect("/?error=yup")

        original_file = "/static/wip/" + file_name
        sugarized_file = "/static/done/" + file_name

    return render_template(
        "index.html",
        original_icon_file=original_file,
        sugarized_icon_file=sugarized_file,
        icon_name=file_name,
        error=error)

@app.route('/randomcolor')
def random_icon_with_color():
    icon_name = request.args.get('filename')
    f = open(os.path.join(done_path, icon_name), "r")
    icon_data = f.read()
    f.close()

    colors = finder.findall(icon_data)[0]
    new_colors = random_color()

    current_stroke_color = stroke_color.format(color=colors[0])
    current_fill_color = fill_color.format(color=colors[1])

    new_stroke_color = stroke_color.format(color=new_colors[0])
    new_fill_color = fill_color.format(color=new_colors[1])

    new_icon = icon_data.replace(
        current_stroke_color,
        new_stroke_color).replace(
        current_fill_color,
        new_fill_color)

    f = open(os.path.join(random_path, icon_name), "w")
    f.write(new_icon)
    f.close()

    return "OK"

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
