import argparse, os, shutil
import libs

'''
Generate a "regression" result from a document.
Obtain the latest_result through "http://127.0.0.1:8000".
From the results obtained, one adoc is generated.
Kick : python3.7 main.py
'''

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def parser():
  parse = argparse.ArgumentParser(description="Generate a func_regression_report.adoc by Dashboard data")
  parse.add_argument("--output_dir", type=str, default=f"{THIS_DIR}/build", help="Project build dir")
  parse.add_argument("--templates_dir", type=str, default=f"{THIS_DIR}/templates", help="Project templates dir")
  parse.add_argument("--project", type=str, default="Test_Ongoing", help="Project name")
  parse.add_argument("--url", "-u",  help="Confluence URL", type=str, default="")
  return parse

def main(**kwargs):

  if os.path.isdir( kwargs.get('output_dir') ):
    shutil.rmtree( kwargs.get('output_dir') )

  libs.generateHtml.main(**kwargs)
  libs.generateChart.main(**kwargs)
  libs.generate_pdf.main(**kwargs)
  libs.sendingEmail.main(**kwargs)

if __name__ == "__main__":
  args = vars(parser().parse_args())
  main(**args)