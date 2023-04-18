import requests
import argparse
import jinja2
import json, os

THIS_DIR=os.path.dirname(os.path.abspath(__file__))

def parser():
  parse = argparse.ArgumentParser("Get Data")
  parse.add_argument("--output_dir", "-od",  help="Output Directory", default=f"{THIS_DIR}/../build", type=str)
  parse.add_argument("--templates_dir", "-td",  help="Templates Directory", default=f"{THIS_DIR}/../templates", type=str)
  parse.add_argument("--project", "-p",  help="Project Name", required=True, type=str)
  parse.add_argument("--url", "-u",  help="Confluence URL", type=str, default="")
  return parse

def getData(**kwargs):
  result = requests.get(f'http://127.0.0.1:8000/get_report/{kwargs["project"]}')
  weekly = requests.get(f'http://127.0.0.1:8000/get_weekly/{kwargs["project"]}')
  kwargs.update( { "result" : result.json(), "weekly" : weekly.json()} )
  if kwargs.get('url') != "":
    kwargs.get("result")["CONFLUENCE"] = kwargs.get('url')
  return {"result" : kwargs.get("result") , "weekly" : kwargs.get("weekly")}

def main(**kwargs):
  if not os.path.isdir( kwargs.get('output_dir') ):
    os.makedirs( kwargs.get('output_dir') )
  with open(f"{kwargs.get('templates_dir')}/email.html.jinja2") as f:
    template = jinja2.Template("".join(f.readlines()))
  rendered_template = template.render( **getData( **kwargs ) )
  with open(f"{kwargs.get('output_dir')}/body.html", 'w') as f:
    f.write(rendered_template)

if __name__ == "__main__":
  args = parser().parse_args()
  main(**vars(args))