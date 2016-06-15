import logging
import webbrowser
from tempfile import NamedTemporaryFile
import ujson as json

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>lsd-cli visualization</title>
  <link href='http://cdn.jsdelivr.net/yasr/2.4.6/yasr.min.css' rel='stylesheet' type='text/css'/>
</head>
<body>
  <div id="yasr"></div>

  <!-- required -->
  <script src='http://cdn.jsdelivr.net/jquery/1.11.1/jquery.min.js'></script>

  <!-- optional, used by the raw-response output (removing dependency will disable this plugin) -->
  <script src="http://cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/codemirror.min.js"></script>

  <!-- optional, used by the table output (removing dependency will disable this plugin) -->
  <script src="http://cdn.datatables.net/1.10.4/js/jquery.dataTables.min.js"></script>

  <!-- optional, used by the pivot output (removing dependency will disable this plugin) -->
  <script src="http://cdnjs.cloudflare.com/ajax/libs/pivottable/1.3.0/pivot.min.js"></script>
  <!-- required for the pivot plugin to work. (specific feature from jquery-ui needed: sortable) -->
  <script src="http://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js"></script>
  <!-- The D3 renderer of the pivot plugin (used for the treemap). (removing dependency will disable this plugin) -->
  <script src="http://cdnjs.cloudflare.com/ajax/libs/d3/3.4.13/d3.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/1.3.0/d3_renderers.min.js"></script>
  <!-- The google chart renderers.  See the plugin settings on how to disable these renderers -->
  <script type="text/javascript" src="https://www.google.com/jsapi"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/1.3.0/gchart_renderers.min.js"></script>

  <!-- required, the actual YASR codebase -->
  <script src='http://cdn.jsdelivr.net/yasr/2.4.6/yasr.min.js'></script>

  <script type="text/javascript">
    YASR.useGoogleCharts = true;
    //now instantiate the YASR object
    var yasr = YASR(document.getElementById("yasr"));
    //and load some test
    var sparqlJson = %(json_string)s;
    yasr.setResponse(sparqlJson);
  </script>
</body>
'''

def visualise(sparql_data):
    json_string = json.dumps(sparql_data, indent=4)

    with NamedTemporaryFile(delete=False, suffix=".html") as tempf:
        data = TEMPLATE % locals()
        tempf.write(bytes(data, 'UTF-8'))
        logging.debug("Opening %s", tempf.name)
        tempf.flush()

        webbrowser.open('file://' + tempf.name, new=0, autoraise=True)
