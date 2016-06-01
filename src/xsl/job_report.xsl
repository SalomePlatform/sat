<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" />
<xsl:template match="/">
	
<head>  
    <title>SAlomeTools log</title>
    <style type="text/css">
        table       { 
                      margin:1px;
                      padding:1px;
                      border-collapse:collapse;
                      empty-cells : show;
                    }
        td          { vertical-align : center;}
        h1          { text-align : center; }
        .legend     { font-weight : bold;
                      text-align : center;
                    } 
        .def        { font-family: Arial, Verdana, "Times New Roman", Times, serif;}
        hr.note     { color: #BFBFBF; }
        .note       { text-align : right; font-style: italic; font-size: small; }
        div.release { -moz-column-count: 2;
                      overflow: auto;
                      max-height: 250px;
                    }
    </style>
</head>
	<body class="def" bgcolor="aliceblue">
		<table border="1">
			<xsl:for-each select="JobsReport/hosts/@*">
				<tr bgcolor="aliceblue" width="2">
					<td><xsl:value-of select="concat('host ', name(), ' / port ', .)"/></td>
					<xsl:for-each select="JobsReport/job">
						<xsl:choose>
						    <xsl:when test="host=concat(name(), ':', .)">
							    <td>XXX</td>
						    </xsl:when>
						    <xsl:otherwise>
							    <td>YYY</td>
						    </xsl:otherwise>
						</xsl:choose>
					</xsl:for-each>
				</tr>
			</xsl:for-each>
		</table>
	</body>
</xsl:template>
</xsl:stylesheet>
