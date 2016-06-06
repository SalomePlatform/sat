<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<html>
<head>
<title>Jobs Report</title>
<style type="text/css">
    <!-- styles for commands results -->
    .OKday        { background-color:#20FF20; }
    .OKweek       { background-color:#90EE90; font-size: 11px; }
    .OKmonth      { background-color:#90EE90; font-size: 10px; }
    .OKold        { background-color:#90EE90; font-size: 9px; }

    .KOday        { background-color:#F20000; }
    .KOweek       { background-color:#FFC0CB; font-size: 11px; }
    .KOmonth      { background-color:#FFC0CB; font-size: 10px; }
    .KOold        { background-color:#FFC0CB; font-size: 9px; }

    .KFday        { background-color:#FFA500; }
    .KFweek       { background-color:#FAC86D; font-size: 11px; }
    .KFmonth      { background-color:#FAC86D; font-size: 10px; }
    .KFold        { background-color:#FAC86D; font-size: 9px; }

    .NAday        { background-color:#BBBBBB; }
    .NAweek       { background-color:#BFBFBF; font-size: 11px; }
    .NAmonth      { background-color:#CACACA; font-size: 10px; }
    .NAold        { background-color:#CFCFCF; font-size: 9px; }

    .label        { font-weight: bold; }

    <!-- styles for links in matrix -->
    .OK2          { color:#00AA00; }
    .KO2          { color:#FF0000; }
    .KF2          { color:#509050; }
    .NA2          { color:#BBBBBB; }
    .OK2day       { color:#00AA00; font-weight: bold; }
    .KO2day       { color:#FF0000; font-weight: bold; }
    .KF2day       { color:#FF8000; font-weight: bold; }
    .NA2day       { color:#BBBBBB; font-weight: bold; }

    .new          { background-color:#FF5500; }
    .day          { background-color:#F0E25A; font-size: small; }
    .week         { background-color:#E0E0E0; font-size: small; }
    .month        { background-color:#C0C0C0; font-size: small; }
    .old          { background-color:#A0A0A0; font-size: small; }
    .lnk          { font-size: 12px; }
    .lnk a        { text-decoration: none; }
    .note         { text-align : right; font-style: italic; font-size: small; }
    table.legend  { margin:0px;
                    padding:5px;
                    border-collapse:collapse;
                    empty-cells : show;
                    border : solid 1px;
                  }
    table.summary { width : 100%;
                    margin:0px;
                    padding:0px;
                    border-collapse:collapse;
                    empty-cells : show;
                    border : solid 1px;
                  }
    td.summary    { border : solid 0px; font-size: medium; }
    td            { border : solid 1px; }
    td.small      { border : solid 1px; font-size: small; }
    th            { font-size: small; border: solid 1px;  }
    h2            { text-align : center; }
    h3            { text-align : left; font-size: small; font-weight: normal; }
    h4            { text-align : left; font-size: small; font-weight: bold; display: inline; }
    h_err         { text-align : left; font-size: small; font-weight: normal; display: inline; 	color: red; }
    .legend       { text-align : center; } 
    .def        { font-family: Arial, Verdana, "Times New Roman", Times, serif;}
   
</style>

<xsl:if test="//JobsReport/infos/@JobsCommandStatus='running'">
  <meta http-equiv="refresh" content="1"></meta>
</xsl:if>

<script language="JavaScript"><![CDATA[
      function Toggle(id) {
        collapseall();
        var element = document.getElementById(id);

         if ( element.style.display == "none" )
            element.style.display = "block";
         else 
            element.style.display = "none";
      }

      function collapseall() {
        var x=document.getElementsByTagName("div");
        for (i=0;i<x.length;i++)
        {
            if ( x[i].id != "matrix" )
                x[i].style.display = "none";
        }
      }
    ]]>
</script>

</head>

<body class="def">
    <table width="100%">
	<tr>
	    <td class="summary">
		<h2>Jobs Report</h2>
	    </td>
	    <td class="summary" align="right" valign="bottom" width="300">
		<xsl:for-each select="//JobsReport/infos">
		  <span class="note"><xsl:value-of select="@name" />: <xsl:value-of select="@value" /></span>
		</xsl:for-each>
	    </td>
	</tr>
    </table>
       
    <div id="matrix">
    <table class="summary">
      <!-- header -->
      <tr bgcolor="#9acd32">
      <th></th>
      <xsl:for-each select="//JobsReport/applications/application">
        <xsl:sort select="@name" />
	<th><xsl:value-of select="@name" /></th>
      </xsl:for-each>
      </tr>
      
      <!-- for all hosts -->
      <xsl:for-each select="//JobsReport/distributions/dist">
        <xsl:sort select="@name" />
	<xsl:variable name="curr_distname" select="@name" />
	<tr>
	<td align="center"><xsl:value-of select="$curr_distname" /></td>
	<!-- for all jobs -->
	<xsl:for-each select="//JobsReport/applications/application">
	  <xsl:sort select="@name" />
	  <xsl:variable name="curr_appli" select="@name" />
	  <td align="center" class="small">
	      <!-- get the job for current host and current appli -->
	      <xsl:for-each select="//JobsReport/jobs/job">
		  <xsl:sort select="@name" />
		  <xsl:if test="application/.=$curr_appli and distribution/.=$curr_distname">
		      <a href="#"><xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
		      <xsl:value-of select="@name"/></a>&#160; : 
		      <xsl:value-of select="state/." />
		      <br/>
		  </xsl:if> 
		  
	      </xsl:for-each>
	  </td>
	</xsl:for-each>
	</tr>
      </xsl:for-each>
    </table>
    
    <h3>
    <xsl:choose>
	<xsl:when test="//JobsReport/infos/@JobsCommandStatus='running'">
	    Command status : running <img src="running.gif"></img>
	</xsl:when>
	
	<xsl:otherwise>
	    Command status : finished
	</xsl:otherwise>
    </xsl:choose>
    </h3>
    </div>

    
    <!-- Loop over the jobs in order to find what job was called in the link "onclick". Display information about that job -->
    <xsl:for-each select="//JobsReport/jobs/job">
      <xsl:variable name="curr_job_name" select="@name" />
      <div style="display:none"><xsl:attribute name="id"><xsl:value-of select="@name"/></xsl:attribute>
	  <!-- Display job name -->
	  <h4>Name : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/@name"/>
	  <br/>
	  <!-- Display the job attributes -->
	  <h4>Hostname/port : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/host"/>/<xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/port"/>
	  <br/>
	  <h4>User : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/user"/>
	  <br/>
	  <h4>Timeout : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/timeout"/>
	  <br/>
	  <h4>Begin : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/begin"/>
	  <br/>
	  <h4>End : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/end"/>
	  <br/>
	  <h4>Commands : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/commands"/>
	  <br/>
	  <h4>Out : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/out"/>
	  <br/>
	  <h4>Err : </h4><h_err><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/err"/></h_err>
      </div>
    </xsl:for-each>

</body>

</html>
</xsl:template>
</xsl:stylesheet>