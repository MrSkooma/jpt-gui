import base64
import os.path

import jpt
import jpt.distributions.univariate
import dash_bootstrap_components as dbc
import dash
from dash import dcc, Input, Output
import json
import components as c
import sys, getopt

'''
This is the main Programming where the Server will be started and the navigator are constructed.
'''

import os
jupyterhub_prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX')
dash_prefix = f"{jupyterhub_prefix}proxy/8050/" if jupyterhub_prefix else '/'



pre_tree = ""
temp_tree = False
app_tags = dict(debug=True, dev_tools_hot_reload=False,)
if len(sys.argv) > 1:
    opts, args = getopt.getopt(sys.argv[1:], "f:h:p:t:", ["file=", "host=", "port=", "help", "tree="])
    for opt, arg in opts:
        if opt in ("-f", "--file"):
            pre_tree = ""
            if not os.path.isfile(arg):
                raise ValueError(f"file {arg} dose not exist.")
            pre_tree = arg
        elif opt in ("-h", "--host"):
            app_tags.update({"host", str(arg)})
        elif opt in ("-p", "--port"):
            app_tags.update(dict(port=int(arg)))
        elif opt == "--help":
            print("-t, --tree you can preload a tree with its path from the app.py directory \n -h, --host you can change the IP of the GUI \n -p --port you can change the port of the GUI \n Default Address is (http://127.0.0.1:8050/)")
            exit(0)
        elif opt in ("-t", "--tree"):
            temp_tree = True
            pre_tree = arg


app = dash.Dash(__name__, use_pages=True, prevent_initial_callbacks=False, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                )


navbar = dbc.Navbar(
            dbc.Container([
                dbc.Row(dbc.NavbarBrand("Joint Probability Trees", className="ms-2")),
                dbc.Row(dbc.NavItem(dcc.Upload(children=dbc.Button("🌱", n_clicks=0, className=""),
                                               id="upload_tree"))),
                dbc.Row([
                    dbc.Col([
                        dbc.Nav(c.gen_Nav_pages(dash.page_registry.values(), ["Empty"]), navbar=True,)
                    ])
                ], align="center")
            ]), color="dark", dark=True,
        )

def server_layout():
    '''
        Returns the Dash Strucktur of the JPT-GUI where the pages are Contained
    :return: Dash Container of the Static Page Elements
    '''
    return dbc.Container(
        [
            dbc.Row(navbar),
            dash.page_container,
            dcc.ConfirmDialog(id="tree_change_info", message="Tree was changed!"),
            dcc.Location(id="url")
        ]
    )

app.layout = server_layout


@app.callback(
    Output('tree_change_info', 'displayed'),
    Output('url', "pathname"),
    Input("upload_tree", "contents"),
)
def tree_update(upload):
    '''
        Loads a chosen jpt Tree and Refresehs to home page
        if it dosnt load nothing happens (Empty page default back to home)
    :param upload: the Paramter Dash generats from chosen a File
    :return: if the Tree was Changed and which page to load
    '''
    if upload is not None:
        try:
            content_type, content_string = upload.split(',')
            decoded = base64.b64decode(content_string)
            content_decided_string = decoded.decode("utf-8")
            io_tree = jpt.JPT.from_json(json.loads(decoded))
        except Exception as e:
            print(e)
            return False,  f"{dash_prefix}"
        c.in_use_tree = io_tree
        c.priors = io_tree.priors
        return True,  f"{dash_prefix}"
    return False,  f"{dash_prefix}"


class CustomDecoder(json.JSONDecoder):
    def decode(self, s):
        # Swap quotes for valid JSON snytax
        s = s.replace("'", "\"")
        # Replace "inf" with "null" in the JSON string before parsing
        s = s.replace('None', 'null').replace('inf', '"inf"')
        # Use the default JSON decoder to parse the modified string
        parsed = super().decode(s)
        # Replace any "null" values with positive infinity
        return self.replace_inf(parsed)

    def replace_inf(self, obj):
        if isinstance(obj, dict):
            return {key: self.replace_inf(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_inf(item) for item in obj]
        elif obj == '"inf"':
            return float('inf')
        return obj

def run():
    if pre_tree != "":
        tree_data = pre_tree
        try:
            tree = open(pre_tree, "rb")
            tree_data = tree.read()
            tree.close()

            io_tree = jpt.JPT.from_json(json.loads(tree_data, cls=CustomDecoder))
            c.in_use_tree = io_tree
            c.priors = io_tree.priors
            if temp_tree:
                os.remove(pre_tree)


        except json.decoder.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(f"Problematic JSON substring: {tree_data[max(0, e.pos-10): e.pos + 10]}")
        except Exception:
            print("File could not be read")
            exit(1)

    app.run(**app_tags)

def jrun():
    app.run()
if __name__ == '__main__':
    run()


