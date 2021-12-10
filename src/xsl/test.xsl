<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<html>
<head>
<title>Tests of <xsl:value-of select="//product/@name" /></title>
<style type="text/css">
    .def        { font-family: monospace, Arial, Verdana, "Times New Roman", Times, serif;}
    .OK         { background-color:#00FF00; }
    .KO         { background-color:#FF0000; }
    .KF         { background-color:#FFA500; }
    .NA         { background-color:#BBBBBB; }
    .PASS       { background-color:#00FF00; }
    .FAILED     { background-color:#F22000; }
    .TIMEOUT    { background-color:#DFFF00; }
    .OK2        { color:#00FF00; }
    .KO2        { color:#F22000; font-weight: bold; }
    .NA2        { color:#BBBBBB; }
    .CHECK2     { color:#FFA500; }
    .ok         { color:#00AA00; }
    .ko         { color:#AA0000; }
    .new        { background-color:#FF5500; }
    .undercontrol { background-color:#AA0000; }
    .ignored    { color:#A0A0A0; }
    div.pqlist  { -moz-column-count: 5;
                  overflow: auto;
                  max-height: 250px;
                }
    table.pq    { width: 100%;
                  margin:0px;
                  padding:0px;
                  border-collapse: collapse;
                  empty-cells: show;
                  border-style: hidden;
                }
    table       { margin:0px;
                  padding:0px;
                  border-collapse:collapse;
                  empty-cells: show;
                  border: solid 1px;
                }
    td.KO2      { border: solid 1px black; padding: 0px; }
    td.OK2      { border: solid 1px black; padding: 0px; }
    td          { border: solid 1px black; padding: 1px; }
    h2          { text-align: center; }
    .legend     { font-weight: bold;
                  text-align: center;
                }
    span.covered { display:-moz-inline-box; display: inline-block;
                  height:18px;
                  vertical-align:top;
                  background: #00df00; 
                }
    span.uncovered { display:-moz-inline-box; display: inline-block;
                  height:18px;
                  vertical-align:top;
                  background: #df0000; 
                }
    span.ignored { display:-moz-inline-box; display: inline-block;
                  height:18px;
                  vertical-align:top;
                  background: #dfff00;
                }
    span.knownfailure { display:-moz-inline-box; display: inline-block;
                  height:18px;
                  vertical-align:top;
                  background: #ffa500;
                }
    span.notApplicable { display:-moz-inline-box; display: inline-block;
                  height:18px;
                  vertical-align:top;
                  background: #bbbbbb;
                }
    span.zero   { color: #A0A0A0; }
    a.node      { color: #0000FF }

</style>
<script language="JavaScript"><![CDATA[
      function Toggle(id) {
        collapsealltext();
        var element = document.getElementById(id);

        if ( element.style.display == "none" )
          element.style.display = "block";
        else 
          element.style.display = "none";
      }

        function collapseall() {
          var divlist = document.getElementsByName("mod");
          for (i = 0; i < divlist.length; i++)
          {
              divlist[i].style.display = "none";
          }
          }
        function collapsealltext() {
          var divlist = document.getElementsByName("text");
          for (i = 0; i < divlist.length; i++)
          {
              divlist[i].style.display = "none";
          }          
      }

    ]]></script>
</head>

<body class="def">
    
  <xsl:apply-templates select="//product" mode="test" />

  <br/>
  <br/>

  </body>
  </html>
</xsl:template>

<xsl:template match="product" mode="test">

  <a>
  <xsl:attribute name="href"><xsl:value-of select="/salome/product/@history_file"/></xsl:attribute>
  history view
  </a>

  <h3>Tests</h3>
    
  <xsl:for-each select="tests/testbase">
    <b>test base <xsl:value-of select="@name" /></b><br/><br/>
    <a name="test"/>
    <xsl:apply-templates select="." mode="test-base" />
  </xsl:for-each>

</xsl:template>

<xsl:template match="testbase" mode="test-base">
  <table>
    <!-- Header -->
    <tr bgcolor="#9acd32">
      <th width="150">grid</th>
      <th width="100">success</th>
      <th width="200"></th>
      <th width="100">total</th>
      <th width="100">pass</th>
      <th width="100">failed</th>
      <th width="100">timeout</th>
      <th width="100">known failures</th>
      <th width="100">not run</th>
      <th width="100">N/A</th>
      <th width="100">Time</th>
    </tr>
        
    <xsl:for-each select="./grid">
    <xsl:if test="@executed_last_time='yes'">
     
      <xsl:variable name="total" select="count(.//test)"/>
      <xsl:variable name="failureCount" select="count(.//test[@res='KO'])"/>
      <xsl:variable name="successCount" select="count(.//test[@res='OK'])"/>
      <xsl:variable name="timeoutCount" select="count(.//test[@res='TIMEOUT'])"/>
      <xsl:variable name="knownFailures" select="count(.//test[@res='KF'])"/>
      <xsl:variable name="notApplicable" select="count(.//test[@res='NA'])"/>
      <xsl:variable name="ignoreCount" select="$total - $successCount - $failureCount - $knownFailures - $notApplicable"/>
      <xsl:variable name="successRate" select="$successCount div $total"/>

      <tr>
        <td><a href="#test" class="node" title="voir">
          <xsl:attribute name="onclick">javascript:collapseall();Toggle('mod_<xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/>');</xsl:attribute>
          <xsl:attribute name="id">img_<xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="@name"/>&#160;</a>
        </td>

        <td align="right">
          <xsl:call-template name="display-percent">
            <xsl:with-param name="value" select="$successRate"/>
          </xsl:call-template>
        </td>
        <td width="210px" align="center">
          <!-- Progress bar -->
          <xsl:if test="round($successCount * 200 div $total) != 0">
            <span class="covered">
              <xsl:attribute name="style">width:<xsl:value-of select="round($successCount * 200 div $total)"/>px</xsl:attribute>&#160;
            </span>
          </xsl:if>
          <xsl:if test="round($failureCount * 200 div $total) != 0">
            <span class="uncovered">
              <xsl:attribute name="style">width:<xsl:value-of select="round($failureCount * 200 div $total)"/>px</xsl:attribute>&#160;
            </span>
          </xsl:if>
          <xsl:if test="round($knownFailures * 200 div $total) != 0">
            <span class="knownfailure">
                <xsl:attribute name="style">width:<xsl:value-of select="round($knownFailures * 200 div $total)"/>px</xsl:attribute>&#160;
            </span>
          </xsl:if>
          <xsl:if test="round($notApplicable * 200 div $total) != 0">
            <span class="notApplicable">
                <xsl:attribute name="style">width:<xsl:value-of select="round($notApplicable * 200 div $total)"/>px</xsl:attribute>&#160;
            </span>
          </xsl:if>
          <xsl:if test="round($ignoreCount * 200 div $total) != 0">
            <span class="ignored">
              <xsl:attribute name="style">width:<xsl:value-of select="round($ignoreCount * 200 div $total)"/>px</xsl:attribute>&#160;
            </span>
          </xsl:if>
        </td>
        <td align="right"><xsl:value-of select="$total" /></td>
        <td align="right"><xsl:value-of select="$successCount" /></td>
        <xsl:call-template name="display-count"><xsl:with-param name="value" select="$failureCount"/></xsl:call-template>

        <xsl:call-template name="display-count"><xsl:with-param name="value" select="$timeoutCount"/></xsl:call-template>
        <xsl:call-template name="display-count"><xsl:with-param name="value" select="$knownFailures"/></xsl:call-template>
        <xsl:call-template name="display-count"><xsl:with-param name="value" select="$ignoreCount"/></xsl:call-template>
        <xsl:call-template name="display-count"><xsl:with-param name="value" select="$notApplicable"/></xsl:call-template>
        <td align="right"><xsl:value-of select="format-number(sum(.//test/@exec_time), '0.0')" /></td>
      </tr>
    </xsl:if>
    </xsl:for-each>

    <!-- Summary Row -->
    <xsl:variable name="GrandTotal" select="number(../testbase/@total)"/>
    <xsl:variable name="TotalFailure" select="count(//test[@res='KO'])"/>
    <xsl:variable name="TotalSuccess" select="count(//test[@res='OK'])"/>
    <xsl:variable name="TotalTimeout" select="count(//test[@res='TIMEOUT'])"/>
    <xsl:variable name="TotalKnownFailures" select="count(//test[@res='KF'])"/>
    <xsl:variable name="TotalNA" select="count(//test[@res='NA'])"/>
    <xsl:variable name="TotalIgnore" select="$GrandTotal - $TotalSuccess - $TotalFailure - $TotalKnownFailures - $TotalNA"/>
    <xsl:variable name="TotalSuccessRate" select="$TotalSuccess div $GrandTotal"/>

    <tr bgcolor="#EF9C9C">
      <td>Total</td>
      <td align="right">
        <xsl:call-template name="display-percent">
          <xsl:with-param name="value" select="$TotalSuccessRate"/>
        </xsl:call-template>
      </td>
      <td width="210px" align="center">
        <xsl:if test="round($TotalSuccess * 200 div $GrandTotal) != 0">
          <span class="covered">
            <xsl:attribute name="style">width:<xsl:value-of select="round($TotalSuccess * 200 div $GrandTotal)"/>px</xsl:attribute>&#160;
          </span>
        </xsl:if>
        <xsl:if test="round($TotalFailure * 200 div $GrandTotal) != 0">
          <span class="uncovered">
            <xsl:attribute name="style">width:<xsl:value-of select="round($TotalFailure * 200 div $GrandTotal)"/>px</xsl:attribute>&#160;
          </span>
        </xsl:if>
        <xsl:if test="round($TotalKnownFailures * 200 div $GrandTotal) != 0">
          <span class="knownfailure">
            <xsl:attribute name="style">width:<xsl:value-of select="round($TotalKnownFailures * 200 div $GrandTotal)"/>px</xsl:attribute>&#160;
          </span>
        </xsl:if>
        <xsl:if test="round($TotalIgnore * 200 div $GrandTotal) != 0">
          <span class="ignored">
            <xsl:attribute name="style">width:<xsl:value-of select="round($TotalIgnore * 200 div $GrandTotal)"/>px</xsl:attribute>&#160;
          </span>
        </xsl:if>
      </td>
      <td align="right"><xsl:value-of select="$GrandTotal" /></td>
      <td align="right"><xsl:value-of select="$TotalSuccess" /></td>
      <td align="right"><xsl:value-of select="$TotalFailure" /></td>
      <td align="right"><xsl:value-of select="$TotalTimeout" /></td>
      <td align="right"><xsl:value-of select="$TotalKnownFailures" /></td>
      <td align="right"><xsl:value-of select="$TotalIgnore" /></td>
      <td align="right"><xsl:value-of select="$TotalNA" /></td>
      <td align="right"><xsl:value-of select="format-number(sum(//test/@exec_time), '0.0')" /></td>
    </tr>
  </table>
    
  <br/>
  <!-- Show details -->
  <xsl:for-each select="./grid">
    <xsl:sort select="@name" />
    <xsl:sort select="@session" />

    <div style="display:none" name="mod"><xsl:attribute name="id">mod_<xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/></xsl:attribute>
    Tests of grid <b><xsl:value-of select="@name"/></b>
    <table width="100%">
      <tr bgcolor="#9acd32">
        <th width="100">session</th>
        <th>script</th>
        <th width="100">result</th>
        <th width="100">time</th>
      </tr>

      <xsl:for-each select="./session">
        <xsl:sort select="@name" />

        <tr>
          <td align="center"><xsl:attribute name="rowspan"><xsl:value-of select="count(./test)+count(.//callback)+1" /></xsl:attribute>
            <xsl:value-of select="@name" />
            <br/>(<xsl:value-of select="format-number(sum(./test/@exec_time), '0')" /> s)
          </td>
        </tr>

      <xsl:for-each select="./test">
        <xsl:sort select="@script" />

        <xsl:choose>
          <xsl:when test="count(./callback) != 0">
            <tr>
              <td align="left">
		    <xsl:attribute name="class"><xsl:value-of select="@res" /></xsl:attribute>
		    <a href="#content" class="node">
			    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@script"/>')</xsl:attribute>
			    <xsl:attribute name="title">Click to see the script content</xsl:attribute>
			    <xsl:value-of select="@script" />
		    </a>
		    &#160;
		    <a href="#content" class="node">
			    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@script"/>log')</xsl:attribute>
			    <xsl:attribute name="title">Click to see the execution log</xsl:attribute>
			    log
		    </a>
              </td>
              <td align="center"><xsl:attribute name="class"><xsl:value-of select="@res" /></xsl:attribute><xsl:value-of select="@res" /></td>
              <td align="right"><xsl:value-of select="format-number(@exec_time, '0.0')" /></td>
            </tr>
            <tr>
              <td align="left" colspan="3" class="linkification-disabled"><xsl:value-of select="./callback" /></td>
            </tr>
          </xsl:when>
          <xsl:otherwise>
            <tr>
              <td align="left">
		    <a href="#content" class="node">
			    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@script"/>')</xsl:attribute>
			    <xsl:attribute name="title">Click to see the script content</xsl:attribute>
			    <xsl:value-of select="@script" />
		    </a>
		    &#160;
		    <a href="#content" class="node">
			    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@script"/>log')</xsl:attribute>
			    <xsl:attribute name="title">Click to see the execution log</xsl:attribute>
			    log
		    </a>
              </td>
              <td align="center"><xsl:attribute name="class"><xsl:value-of select="@res" /></xsl:attribute><xsl:value-of select="@res" /></td>
              <td align="right"><xsl:value-of select="format-number(@exec_time, '0.0')" /></td>
            </tr>
          </xsl:otherwise>
        </xsl:choose>
          <xsl:if test="count(./amend) != 0">
            <tr>
              <td class="ko"><b>Amended</b></td>	
              <td align="left" colspan="3"><xsl:value-of select="./amend" /></td>
            </tr>
          </xsl:if>
      </xsl:for-each>
      </xsl:for-each>
    
    </table>
    </div>
  <!--</xsl:if>-->
  </xsl:for-each>
  
  <xsl:for-each select="./grid">
    <xsl:for-each select="./session">
      <xsl:for-each select="./test">
	  <div style="display:none" name="text"><xsl:attribute name="id"><xsl:value-of select="@script"/></xsl:attribute>
	    <PRE><xsl:value-of select="./content"/></PRE>
	  </div>
	  <div style="display:none" name="text"><xsl:attribute name="id"><xsl:value-of select="@script"/>log</xsl:attribute>
	    <PRE><xsl:value-of select="./out"/></PRE>
	  </div>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:for-each>
  
</xsl:template>

<xsl:template name="display-percent">
    <xsl:param name="value"/>
    <xsl:value-of select="format-number($value, '00.00 %')"/>
</xsl:template>

<xsl:template name="display-count">
    <xsl:param name="value"/>
    <td align="right">
    <xsl:if test="$value &gt; 0">
        <xsl:value-of select="$value"/>
    </xsl:if>
    <xsl:if test="$value = 0"><span class="zero">0</span></xsl:if>
    </td>
</xsl:template>

</xsl:stylesheet>
