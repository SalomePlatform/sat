<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" /> 
<!-- encoding="utf-8" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>-->
<xsl:template match="/">

<head>  
  <title>SAlomeTools log</title>
  <style type="text/css">
      table       { width : 100%;
                    margin:1px;
                    padding:1px;
                    border-collapse:collapse;
                    empty-cells : show;
                  }
      td          { vertical-align : center; padding: 10px; }
      h1          { text-align : center; font-style: italic; font-size: 20px; }
      .legend     { font-weight : bold; text-align : center; } 
      .def        { font-family: monospace, Arial, Verdana, "Times New Roman", Times, serif;}
      hr.note     { color: #BFBFBF; }
      .note       { text-align : right; font-style: italic; font-size: small; }
      div.release { -moz-column-count: 2; overflow: auto; max-height: 250px; }
      .OK2        { color:#00AA00; }
      .KO2        { color:#FF0000; }
  </style>
  <script language="JavaScript"><![CDATA[
      function Toggle(id) {
        var element = document.getElementById(id);

        if ( element.style.display == "none" )
            element.style.display = "block";
        else 
            element.style.display = "none";
       }
]]>
  </script>
</head>

<body class="def" bgcolor="aliceblue">
  <h1><img src="LOGO-SAT.png"/></h1>
  <table border="1">
    <tr>
      <xsl:for-each select="SATcommand/Site/@*">
        <td bgcolor="LightBlue">
          <b><xsl:value-of select="name(.)"/></b>
        </td>
      </xsl:for-each>
    </tr>
    <tr>
      <xsl:for-each select="SATcommand/Site/@*">  
        <td bgcolor="Beige"><xsl:value-of select="."/></td>
      </xsl:for-each>
    </tr>
  </table>
  
  <h1>command's internal traces
  <a href="#">
        <xsl:attribute name="onclick">javascript:Toggle('log')</xsl:attribute>
        <xsl:attribute name="title">Click to expand or collapse the command log</xsl:attribute>
        expand / collapse
  </a>
  </h1>
  
  <div style="display:none"><xsl:attribute name="id">log</xsl:attribute>
      <PRE><xsl:value-of select="SATcommand/Log"/></PRE>
  </div>
  
  <h1>Links</h1>
  <table border="1">
    <xsl:for-each select="SATcommand/Links/link">
      <tr>
        <td bgcolor="Beige">
          <xsl:if test="@passed='0'">
            <a>
              <xsl:attribute name="title">Click for more information</xsl:attribute>
              <xsl:attribute name="class">OK2</xsl:attribute>
              <xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
              <xsl:value-of select="@command"/>
            </a>
          </xsl:if>
          <xsl:if test="@passed!='0'">
            <a>
              <xsl:attribute name="title">Click for more information</xsl:attribute>
              <xsl:attribute name="class">KO2</xsl:attribute>
              <xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
              <xsl:value-of select="@command"/>
            </a>
          </xsl:if>
        </td>
        <td bgcolor="LightBlue">
          <xsl:value-of select="@launchedCommand"/>
        </td>
      </tr>
    </xsl:for-each>
    
  </table>
  
  <h1>output 
  <a target="_blank">
    <xsl:attribute name="title">Click to open in an editor</xsl:attribute>
    <xsl:attribute name="href"><xsl:value-of select="SATcommand/OutLog"/></xsl:attribute>
    <xsl:attribute name="download"><xsl:value-of select="SATcommand/OutLog"/></xsl:attribute>
    log
  </a>
  </h1>
  <xsl:variable name="txtLog">
    <xsl:value-of select="SATcommand/OutLog"/>
  </xsl:variable>
  <iframe src="{$txtLog}" frameborder="0" class="center" width="98%" height="600" scrolling="yes"></iframe>
  <!--<iframe src="{$txtLog}" frameborder="0" class="center" width="98%" height="600" scrolling="yes"></iframe>-->
</body>
</xsl:template>

</xsl:stylesheet>
