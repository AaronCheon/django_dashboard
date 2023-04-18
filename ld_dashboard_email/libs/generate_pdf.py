import argparse, os, subprocess, json, requests
from jinja2 import Template, Environment, FileSystemLoader

'''
Generate a "regression" result from a document.
Obtain the latest_result through "http://127.0.0.1:8000".
From the results obtained, one adoc is generated.
Kick : python3.7 report_regression.py
'''

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def parser():
  parse = argparse.ArgumentParser(description="Generate a func_regression_report.adoc by Dashboard data")
  parse.add_argument("--output_dir", type=str, default=f"{THIS_DIR}/../build", help="Project name")
  parse.add_argument("--templates_dir", type=str, default=f"{THIS_DIR}/../templates", help="Project name")
  parse.add_argument("--project", type=str, default="Test_Ongoing", help="Project name")
  return parse


def get_requests(target : str, **kwargs):
  return requests.get(f'http://127.0.0.1:8000/{target}/{ kwargs.get("project") }').json()

def render_adoc(**kwargs):
  with open( kwargs.get('attach_source'), 'r' ) as f_jinja:
    jinja_text = Template(f_jinja.read())
  return jinja_text.render( **kwargs )

def render_html(**kwargs):
  subprocess.check_output( f"asciidoctor --verbose -d book -a stylesheet! -a header! -a last-update-label! -o {kwargs.get('email_attach_html')} {kwargs.get('email_attach_adoc')}".split(" ") ).decode('utf-8')
def render_pdf(**kwargs):
  subprocess.check_output( f"prince --no-network --javascript -s {kwargs.get('templates_dir')}/css/common.css -s {kwargs.get('templates_dir')}/css/style.css -o {kwargs.get('email_attach_pdf')} {kwargs.get('email_attach_html')}".split(" ") ).decode('utf-8')

def get_data_ld_dashboard(port ,project):
  return json.loads(subprocess.check_output(f"curl -X GET http://127.0.0.1:{port}/get_report/{project}".split(" ")).decode('utf-8').replace('\'',''))

def main(**kwargs):

  if not os.path.isdir( kwargs.get('output_dir') ):
    os.makedirs( kwargs.get('output_dir') )

  kwargs.update(
    email_attach_adoc = f"{ kwargs.get('output_dir') }/email.attach.adoc",
    email_attach_html = f"{ kwargs.get('output_dir') }/email.attach.html",
    email_attach_pdf  = f"{ kwargs.get('output_dir') }/email.attach.pdf"
  )

  kwargs.update( attach_source = f"{ kwargs.get('templates_dir') }/email.attach.adoc.jinja" )
  kwargs.update( get_requests(target="get_report", **kwargs) )
  kwargs.update( get_requests(target="get_weekly", **kwargs) )

  with open( kwargs.get('email_attach_adoc'), 'w') as f_adoc:
    f_adoc.write(render_adoc(**kwargs))

  render_html(**kwargs)
  render_pdf(**kwargs)


if __name__ == "__main__":
  args = vars(parser().parse_args())
  main(**args)