'''
Created on 02.02.2014

@author: hm
'''
import unittest
from webbasic.wikimediaconverter import MediaWikiConverter

class Test(unittest.TestCase):

    def testBasic(self):
        wiki = MediaWikiConverter()
        self.assertEqual(3, wiki.countPrefix("*** hello", "*"))
        
    def testConvertText(self):
        wiki = MediaWikiConverter()
        self.assertEquals("a &lt; b &amp; b &gt;= c",
            wiki.convertBlock("a < b & b >= c"))
        self.assertEquals("this is <b><i>bold and italic</i></b> <b><i>2</i></b>",
            wiki.convertBlock("this is '''''bold and italic''''' '''''2'''''"))
        self.assertEquals("<b>a</b> &lt; <b>b</b> &amp; <i>b</i> &gt;= <i>c</i>",
            wiki.convertBlock("'''a''' < '''b''' & ''b'' >= ''c''"))
        
    def testExternalLink(self):
        wiki = MediaWikiConverter()
        self.assertEquals('x<a href="http://x.com">http://x.comy</a>',
            wiki.convertBlock("x[http://x.com]y"))
        self.assertEquals('x<a href="https://s.de?page=1&id=33">links</a> and more',
            wiki.convertBlock("x[https://s.de?page=1&id=33 link]s and more"))

    def testSimpleLink(self):
        wiki = MediaWikiConverter()
        self.assertEquals('<a href="http://x.com?page=1&id=3">http://x.com?page=1&amp;id=3</a> abc',
            wiki.convertBlock("http://x.com?page=1&id=3 abc"))
        
    def testNowiki(self):
        wiki = MediaWikiConverter()
        self.assertEquals("2''und dann 3''' ",
            wiki.convertBlock("<nowiki>2''und dann 3'''</nowiki> <nowiki />"))
        
    def testPreTag(self):
        wiki = MediaWikiConverter()
        self.assertEquals('''<pre class="myclass" style="color:red;">
1 &lt; 2
2''
</pre>''',
            wiki.convertBlock('''<pre class="myclass" style="color:red;">
1 < 2
2''
</pre>'''))
        
    def testSpan(self):
        wiki = MediaWikiConverter()
        self.assertEquals('''<span class="myclass" style="color:red;">
1 &lt; 2</span>
<b>fat</b>
<span>anything</span>
''',
            wiki.convertBlock("""<span class="myclass" style="color:red;">
1 < 2</span>
'''fat'''
<span>anything</span>
"""))
    
    def testStrike(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<strike>invalid</strike> <strike>1&gt;2</strike>",
            wiki.convertBlock("<strike>invalid</strike> <strike>1>2</strike>"))
        
    def testBr(self):
        wiki = MediaWikiConverter()
        self.assertEquals("a<br />b<br/>c",
            wiki.convertBlock("a<br />b<br/>c"))

    def testCode(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<code>grep -i hello *.txt &gt;hits</code>",
            wiki.convertBlock("<code>grep -i hello *.txt >hits</code>"))
        
    def testIns(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<ins>Gambler&amp;Strike</ins>",
            wiki.convertBlock("<ins>Gambler&Strike</ins>"))
        
    def testBlockquote(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<blockquote>Gambler&amp;Strike</blockquote>",
            wiki.convertBlock("<blockquote>Gambler&Strike</blockquote>"))
       
    def testComment(self):
        wiki = MediaWikiConverter()
        self.assertEquals("x&lt;2&amp;x&gt;1<!--Gambler&Strike-->",
            wiki.convertBlock("x<2&x>1<!--Gambler&Strike-->"))
         
    def testTt(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<tt>Gambler&amp;Strike</tt>",
            wiki.convertBlock("<tt>Gambler&Strike</tt>"))
         
    def testSmall(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<small>Gambler&amp;Strike</small>",
            wiki.convertBlock("<small>Gambler&Strike</small>"))
         
    def testBig(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<big>Gambler&amp;Strike</big>",
            wiki.convertBlock("<big>Gambler&Strike</big>"))
         
    def testHeadline(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<h2>title</h2>\n<h3>chapter2</h3>\n", 
            wiki.convert("==title==\n===chapter2==="))

    def testParagraph(self):
        wiki = MediaWikiConverter()
        html = wiki.convert("""line1
is continued
here

'''fat'''
and ''italic''""")
        self.assertEquals("""<p>line1
is continued
here
</p>
<p><b>fat</b>
and <i>italic</i>
</p>
""", html)

    def testHr(self):
        wiki = MediaWikiConverter()
        html = wiki.convert("""line1
----
line2
----""")
        self.assertEquals(html, """<p>line1
</p>
<hr />
<p>line2
</p>
<hr />
""")

    def testIndent(self):
        wiki = MediaWikiConverter()
        html = wiki.convert("""line1
:i 1
::i2
:i3-1
----""")
        self.assertEquals(html, """<p>line1
</p>
<dl><dd>i 1</dd>
<dl><dd>i2</dd>
</dl><dd>i3-1</dd>
</dl>
<hr />
""")

    def testList(self):
        wiki = MediaWikiConverter()
        self.assertEquals("<ul><li>u1</li>\n</ul>\n<ol><li>o2</li>\n</ol>\n<ul><li>u3</li>\n</ul>\n\n",
            wiki.convert("*u1\n#o2\n*u3"))
        html = wiki.convert("""line1
*u1
*u2
*#o2-1
*#*u3-1
**u4
**u5
*u6
----""")
# *u1
#<ul><li>u1</li>
# *u2
#<li>u2
# * #o2-1
#   <ol><li>o2-1
# * # *u3-1
#       <ul><li>u3-1</li></ul>
# </li></ol>
# * *u4
# <ul><li>u4>/li>
# * *u5
# <li>u5</li></ul>
# </li>
# *u6
# <li>u6</li></ul>      
        self.assertEquals("""<p>line1
</p>
<ul><li>u1</li>
<li>u2<ol><li>o2-1<ul><li>u3-1</li>
</ul>
<li>u4</li>
</ol>
<ul><li>u5</li>
</ul>
<li>u6</li>
</ul>

<hr />
""", html)

    def testTable(self):
        wiki = MediaWikiConverter()
        html = wiki.convert("""{|
!head1
!head2
|-
|col1-1
|col1-2
|-
|col2-1
|col2-2
|}""")
        self.assertEquals("""<table><tr>
<th>head1</th>
<th>head2</th>
</tr><tr>
<td>col1-1</td>
<td>col1-2</td>
</tr><tr>
<td>col2-1</td>
<td>col2-2</td>
</tr></table>
""", html)
        
    def testTable2(self):
        wiki = MediaWikiConverter()
        html = wiki.convert("""{|
!head1|head2
|-
|col1-1||col1-2
|-
|col2-1||col2-2
|}""")
        self.assertEquals("""<table><tr>
<th>head1</th>
<th>head2</th>
</tr><tr>
<td>col1-1</td>
<td>col1-2</td>
</tr><tr>
<td>col2-1</td>
<td>col2-2</td>
</tr></table>
""", html)
        
    def testPre(self):
        wiki = MediaWikiConverter()
        html = wiki.convert(""" xml example:
 <book>
 <title>Shy</title><author>J. Clark</author>
 </book>""")
        self.assertEquals("""<pre class="wiki_pre">xml example:
&lt;book&gt;
&lt;title&gt;Shy&lt;/title&gt;&lt;author&gt;J. Clark&lt;/author&gt;
&lt;/book&gt;
</pre>
""", html)        
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testHeadline']
    unittest.main()