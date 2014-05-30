"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi
import codecs
import collections

import webapp2

import simple_identifier
import transliterate


def InputForm(default=''):
  return """
    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80">%s</textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>""" % cgi.escape(default)


def StatsTable():
  return codecs.open('gretil_stats/stats_table.html', 'r', 'utf-8').read()


def _UniqList(expr):
  return list(collections.OrderedDict.fromkeys(expr))


def _DisplayName(metre_name):
  assert isinstance(metre_name, unicode)
  both_names = transliterate.AddDevanagariToIast(metre_name)
  return '<font size="+2">%s</font>' % both_names


MAIN_PAGE_HTML = open('main_page_template.html').read()
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${INPUT_FORM}', InputForm())
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${METRE_STATISTICS}', StatsTable())


common_identifier = simple_identifier.SimpleIdentifier()


class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(MAIN_PAGE_HTML)

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = common_identifier
    results = identifier.IdentifyFromLines(input_verse.split('\n'))

    self.response.write('<html>\n')
    self.response.write('<head><style>\n')
    self.response.write('abbr {border-bottom: 1px dotted black; color:red;}\n')
    self.response.write('.sylL { } \n')
    self.response.write('.sylG { font-weight:bold; } \n')
    self.response.write('.syl- { } \n')
    self.response.write('</style></head>\n')

    self.response.write('<body>\n')
    self.response.write('<p>')
    self.response.write(InputForm(input_verse))
    self.response.write('</p>')

    if results:
      assert isinstance(results, list)
      self.response.write('<p>The metre may be: %s.' %
                          ' OR '.join(_DisplayName(m) for m in results))
    else:
      self.response.write('<p>No metre recognized.</p>')

    self.response.write('\n'.join(['<hr/>',
                                   '<p><i>Debugging output:</i></p>',
                                   '<details>',
                                   '<summary>Reading the input</summary>',
                                   '<pre>',
                                   identifier.DebugRead(),
                                   '</pre>',
                                   '</details>',
                                   '<br/>',
                                   '<details>',
                                   '<summary>Identifying the metre</summary>',
                                   '<pre>',
                                   identifier.DebugIdentify(),
                                   '</pre>',
                                   '</details>']))
    self.response.write('\n')

    if identifier.tables:
      for (name, table) in identifier.tables:
        self.response.write('<p>Reading as %s:</p>' % _DisplayName(name))
        for line in table:
          self.response.write(line)
    self.response.write('</body></html>')


# Handles all requests to sanskritmetres.appspot.com
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/identify', IdentifyPage),
], debug=True)
