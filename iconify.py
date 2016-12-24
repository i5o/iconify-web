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
import subprocess
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import sugariconify
import os
import uuid
from xocolor import random_color

app = Flask(__name__)
script_path = app.root_path
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

            clean_svg = request.form.getlist("clean")
            if clean_svg:
                return redirect(
                    url_for(
                        'index',
                        filename=filename,
                        cleansvg=1))
            else:
                return redirect(
                    url_for(
                        'index',
                        filename=filename))

    return redirect("/?error=yup")


@app.route('/', methods=['GET'])
def index():
    file_name = request.args.get('filename')
    error = request.args.get('error')
    original_file = None
    sugarized_file = None
    python_error = request.args.get('pythonerror')
    clean_svg = request.args.get("cleansvg")
    debug_msg = None

    if not clean_svg:
        clean_svg = 0

    if clean_svg and file_name:
        original_file = os.path.join(wip_path, file_name)
        done_file = os.path.join(done_path, file_name)
        svg_debug = subprocess.check_output(
            ["./svgcleaner", original_file, done_file])

        return render_template(
            "clean.html",
            debug_msg=svg_debug,
            filename=file_name)

    if file_name:
        original_file = os.path.join(wip_path, file_name)
        sugarized_file = os.path.join(done_path, file_name)

        try:
            of = open(original_file, "r")
            svgtext = of.read()
            of.close()

            reload(sugariconify)
            iconify = sugariconify.SugarIconify()
            iconify.create_svgdom(svgtext)
            colors = iconify.get_colors()

            iconify.set_stroke_color(colors[0])
            iconify.set_fill_color(colors[1])
            debug_output = iconify.iconify(original_file, sugarized_file)
            debug = []

            for x in debug_output:
                if x == "\n":
                    continue
                debug.append(x)

            if not debug[0].startswith("\n"):
                debug[0] = "\n" + debug[0]

            span = "<br><span class='glyphicon glyphicon glyphicon-chevron-right' aria-hidden='true'>&nbsp;</span>"
            debug_msg = "\n".join(debug).replace(
                "\n",
                span)

            if debug_msg.endswith(span):
                debug_msg = debug_msg[:-len(span)]

        except Exception as e:
            return redirect("/?error=yup&pythonerror=%s" % str(e))

        original_file = "/static/wip/" + file_name
        sugarized_file = "/static/done/" + file_name

    return render_template(
        "index.html",
        original_icon_file=original_file,
        sugarized_icon_file=sugarized_file,
        icon_name=file_name,
        error=error,
        python_error=python_error,
        debug_msg=debug_msg)


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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(
            app.root_path,
            'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
