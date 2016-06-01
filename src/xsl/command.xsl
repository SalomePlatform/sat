<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" /> <!-- encoding="utf-8" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>-->
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
        td          { vertical-align : center; padding: 15px; }
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
		<h1><img src="LOGO-SAT.png"/></h1>
		<table border="1">
			<tr>
				<xsl:for-each select="SATcommand/Site/@*">
					<td bgcolor="LightBlue">
						<th><xsl:value-of select="name(.)"/></th>
					</td>
				</xsl:for-each>
			</tr>
			<tr>
				<xsl:for-each select="SATcommand/Site/@*">	
					<td bgcolor="Beige"><xsl:value-of select="."/></td>
				</xsl:for-each>
			</tr>
		</table>
		
		<h1>command's internal traces</h1>
		<PRE><xsl:value-of select="SATcommand/Log"/></PRE>
		
		<h1>Links</h1>
		<table border="1">
			<tr>
				<xsl:for-each select="SATcommand/Links/@*">
					<td bgcolor="LightBlue">
						<a title="log">
							<xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
							<xsl:value-of select="name(.)"/>
						</a>
					</td>
				</xsl:for-each>
			</tr>
		</table>
		
		<h1>output</h1>
		PENSER A METTRE UN LIEN POUR OUVRIR LE FICHIER AVEC UN EDITEUR DE TEXTE
		<xsl:variable name="txtLog">
			<xsl:value-of select="SATcommand/OutLog"/>
		</xsl:variable>
		<iframe src="{$txtLog}" frameborder="0" class="center" width="100%" height="1500000" scrolling="no"></iframe>
	</body>
</xsl:template>
</xsl:stylesheet>