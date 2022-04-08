<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<html>
<head>
<title>Jobs <xsl:value-of select="//JobsReport/board/."/> report</title>
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
    .OK2          { color:#00AA00; font-weight: normal;}
    .KO2          { color:#FF0000; font-weight: normal;}
    .KF2          { color:#FF8000; font-weight: normal;}
    .NA2          { color:#BBBBBB; font-weight: normal;}
    .TO2          { color:GoldenRod; font-weight: normal;}
    .RUNNING2     { color:LightSeaGreen; font-weight: bold; }
    .OK2day       { color:#00AA00; font-weight: bold; }
    .KO2day       { color:#FF0000; font-weight: bold; }
    .KF2day       { color:#FF8000; font-weight: bold; }
    .NA2day       { color:#BBBBBB; font-weight: bold; }
    .TO2day       { color:GoldenRod; font-weight: bold; }

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
                    font-size: xx-small;
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
    .def        { font-family: monospace, Arial, Verdana, "Times New Roman", Times, serif;}
   
</style>

<xsl:if test="//JobsReport/infos/@JobsCommandStatus='running'">
  <meta http-equiv="refresh" content="120"></meta>
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
		<h2>Compilation report <xsl:value-of select="//JobsReport/board/."/></h2>
	    </td>
	    <td class="summary" align="right" valign="bottom" width="300">
		<span class="note"><xsl:value-of select="//JobsReport/infos/@name" />: <xsl:value-of select="//JobsReport/infos/@value" /></span>
	    </td>
	</tr>
    </table>

    <a href="#">
	<xsl:attribute name="onclick">javascript:Toggle('legend')</xsl:attribute>
	<xsl:attribute name="title">legend</xsl:attribute>
	legend
    </a>
    <br/>
    <a href="#">
	<xsl:attribute name="onclick">javascript:Toggle('history')</xsl:attribute>
	<xsl:attribute name="title">history</xsl:attribute>
	history
    </a>
    <br/>
    <br/>
    
    <div id="matrix">
    <table class="summary">
      <!-- header -->
      <tr bgcolor="#9acd32">
      <th></th>
      <xsl:for-each select="//JobsReport/applications/application">
        <!--<xsl:sort select="@name" />-->
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
	  <!--<xsl:sort select="@name" />-->
	  <xsl:variable name="curr_appli" select="@name" />
	  <td align="center" class="small">
	      <!-- get the job for current host and current appli -->
	      <xsl:for-each select="//JobsReport/jobs/job">
	      
		  <xsl:sort select="@name" />
		  <xsl:variable name="curr_job_name" select="@name" />
		  <xsl:if test="application/.=$curr_appli and distribution/.=$curr_distname and board/.=//JobsReport/board/.">
		      <!-- Change background color if it is an extra job (not defined in the input csv files) -->
		      <xsl:if test="extra_job/.='yes'">
			  <xsl:attribute name="bgcolor">FFCCCC</xsl:attribute>
		      </xsl:if>
		      <!-- Get job status and put a link -->
		      <xsl:choose>
			    <xsl:when test="state/.='SSH connection KO' or state/.='Cancelled'">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">KO2day</xsl:attribute>
				    <xsl:value-of select="@name"/>
			      </a>
			    </xsl:when>
			    <xsl:when test="contains(state/., 'Not launched')">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">NA2day</xsl:attribute>
				    <xsl:value-of select="@name"/>
			      </a>
			    </xsl:when>
			    <xsl:when test="contains(state/., 'running')">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">RUNNING2</xsl:attribute>
				    <xsl:value-of select="@name"/>
			      </a>
			    </xsl:when>
			    <xsl:when test="contains(state/., 'Finished')">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">OK2day</xsl:attribute>
				    job
			      </a>
			    </xsl:when>
			    <xsl:when test="contains(state/., 'Timeout')">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">TO2day</xsl:attribute>
				    job
			      </a>
			    </xsl:when>
			    <xsl:when test="state/.='Not today'">
			      <a href="#">
				    <xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="@name"/>')</xsl:attribute>
				    <xsl:attribute name="title"><xsl:value-of select="state/."/></xsl:attribute>
				    <xsl:attribute name="class">NA2</xsl:attribute>
				    job
			      </a>
			    </xsl:when>
		      </xsl:choose>
		      <!--<xsl:value-of select="state/." />-->
		      <xsl:if test="not(remote_log_file_path/.='nothing') and state/.!='Not today'">
			     - 
			    <a>
				<xsl:attribute name="title">Begin : <xsl:value-of select="begin/."/>&#xA;End :    <xsl:value-of select="end/."/> </xsl:attribute>
				<xsl:attribute name="href"><xsl:value-of select="remote_log_file_path/."/></xsl:attribute>
				<xsl:if test="res/.='0'">
				   <xsl:attribute name="class">OK2day</xsl:attribute>
				</xsl:if>
				<xsl:if test="res/.!='0'">
				   <xsl:attribute name="class">KO2day</xsl:attribute>
				</xsl:if>
				<xsl:value-of select="host/."/>
				<xsl:if test="port/.!='22'">
				 / <xsl:value-of select="port/."/>
				</xsl:if>
			    </a>
		      </xsl:if>
		    <xsl:if test="state/.='Not today'">
			 - 
			<xsl:for-each select="//JobsReport/jobs/job[@name=$curr_job_name]/history/link">
			<xsl:sort select="@date" order="descending" />
			<xsl:if test="@last='yes'">
			  <h4>
			    <a>
			      <xsl:attribute name="title">
				  <xsl:value-of select="concat(substring(@date, 7, 2), '/', substring(@date, 5, 2), '/', substring(@date,1,4))"/>
			      </xsl:attribute>
			      <xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
			      <xsl:if test="@res='0'">
				  <xsl:attribute name="class">OK2</xsl:attribute>
			      </xsl:if>
			      <xsl:if test="@res!='0'">
				  <xsl:attribute name="class">KO2</xsl:attribute>
			      </xsl:if>
			      <xsl:value-of select="../../host"/>
			    </a>
			  </h4>
			</xsl:if> 
			</xsl:for-each>
		      </xsl:if>
              <!--Add the link to the tests if there is any -->
              <xsl:if test="(test_log_file_path) and (test_log_file_path/*)">
              -     
                <xsl:for-each select="//JobsReport/jobs/job[@name=$curr_job_name]/test_log_file_path/path">
                  <a>
			          <xsl:attribute name="title"><xsl:value-of select="@nb_fails"/> fails</xsl:attribute>
			          <xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
			          <xsl:if test="@res='0'">
				      <xsl:attribute name="class">OK2day</xsl:attribute>
			          </xsl:if>
			          <xsl:if test="@res!='0'">
				      <xsl:attribute name="class">KO2day</xsl:attribute>
			          </xsl:if>
                      test
                  </a>
                </xsl:for-each>
		      </xsl:if>              
		      <br/>
		      

		  </xsl:if>
		  
	      </xsl:for-each>
	      
	      <!-- get the missing jobs -->
	      <xsl:for-each select="//JobsReport/missing_jobs/job">    
		    <xsl:if test="@distribution=$curr_distname and @application=$curr_appli">
			<xsl:attribute name="bgcolor">ffb8b8</xsl:attribute>
		    </xsl:if>
	      </xsl:for-each>
	      <!-- get the missing jobs not today -->
	      <xsl:for-each select="//JobsReport/missing_jobs_not_today/job">    
		    <xsl:if test="@distribution=$curr_distname and @application=$curr_appli">
			<xsl:attribute name="bgcolor">ffdbdb</xsl:attribute>
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
	    Command status : <xsl:value-of select="//JobsReport/infos/@JobsCommandStatus/."/>
	</xsl:otherwise>
    </xsl:choose>
    </h3>
    </div>
    <span class="note">input file: <xsl:value-of select="//JobsReport/@input_file" /></span>

    <!-- Loop over the jobs in order to find what job was called in the link "onclick". Display information about that job -->
    <xsl:for-each select="//JobsReport/jobs/job">
      <xsl:variable name="curr_job_name" select="@name" />
      <div style="display:none"><xsl:attribute name="id"><xsl:value-of select="@name"/></xsl:attribute>
	  <!-- Display job name -->
	  <h4>Name : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/@name"/>
	  <br/>
	  <xsl:if test="//JobsReport/jobs/job[@name=$curr_job_name]/state!='Not today'">
		  <!-- Display the job attributes -->
		  <h4>Hostname/port : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/host"/>/<xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/port"/>
		  <br/>
		  <h4>User : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/user"/>
		  <br/>
          </xsl:if>
	  <!-- Display history -->
	  <h4>History : </h4>
	  <br/>
	  <xsl:for-each select="//JobsReport/jobs/job[@name=$curr_job_name]/history/link">
	    <xsl:sort select="@date" order="descending" />
	    <h4>
	      <a>
		<xsl:attribute name="title">remote log</xsl:attribute>
		<xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
		<xsl:if test="@res='0'">
		    <xsl:attribute name="class">OK2</xsl:attribute>
		</xsl:if>
		<xsl:if test="@res!='0'">
		    <xsl:attribute name="class">KO2</xsl:attribute>
		</xsl:if>
		<xsl:value-of select="@date"/>
	      </a>
	    </h4>
	    <br/>
	  </xsl:for-each>
	  <xsl:if test="//JobsReport/jobs/job[@name=$curr_job_name]/state!='Not today'">
		  <h4>salomeTools path : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/sat_path"/>
		  <br/>
		  <h4>After : </h4>
		  <a href="#">
			<xsl:attribute name="onclick">javascript:Toggle('<xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/after"/>')</xsl:attribute>
			<xsl:attribute name="title">Click to get job information</xsl:attribute>
			<xsl:attribute name="class">OK2</xsl:attribute>
			<xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/after"/>
		  </a>
		  <br/>
		  <h4>Timeout : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/timeout"/>
		  <br/>
		  <h4>Begin : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/begin"/>
		  <br/>
		  <h4>End : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/end"/>
		  <br/>
		  <h4>Out : </h4><PRE><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/out"/></PRE>
		  <br/>
		  <h4>Err : </h4><h_err><PRE><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/err"/></PRE></h_err>
          </xsl:if>
	  <h4>Status : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/state"/>
	  <br/>
	  <h4>Commands : </h4><xsl:value-of select="//JobsReport/jobs/job[@name=$curr_job_name]/commands"/>
	  <br/>
      </div>
    </xsl:for-each>

    <div style="display:none"><xsl:attribute name="id">legend</xsl:attribute>
      <td border="0"> 
	    <tr><td>job</td><td>result</td></tr>
	    <tr><td> <xsl:attribute name="class">OK2day</xsl:attribute>success today</td><td> <xsl:attribute name="class">OK2day</xsl:attribute>success today</td></tr>
	    <tr><td> <xsl:attribute name="class">OK2</xsl:attribute>success not today</td><td> <xsl:attribute name="class">OK2</xsl:attribute>success not today</td></tr>
	    <tr><td> <xsl:attribute name="class">KO2day</xsl:attribute>fail today</td><td> <xsl:attribute name="class">KO2day</xsl:attribute>fail today</td></tr>
	    <tr><td> <xsl:attribute name="class">KO2</xsl:attribute>fail not today</td><td> <xsl:attribute name="class">KO2</xsl:attribute>fail not today</td></tr>
	    <tr><td> <xsl:attribute name="class">TO2day</xsl:attribute>timeout today</td><td> <xsl:attribute name="class">KF2day</xsl:attribute>known failure today</td></tr>
	    <tr><td> <xsl:attribute name="class">RUNNING2</xsl:attribute>running</td><td> <xsl:attribute name="class">KF2</xsl:attribute>known failure not today</td></tr>
	    <tr><td> <xsl:attribute name="class">NA2day</xsl:attribute>To be launched</td></tr>
	    <tr><td> <xsl:attribute name="class">NA2</xsl:attribute>Not today</td></tr>
	    <tr>Missing job: <td> <xsl:attribute name="bgcolor">FFCCCC</xsl:attribute> </td></tr>
	    <tr>Extra job: <td> <xsl:attribute name="bgcolor">FFCCCC</xsl:attribute> Job name </td></tr>
	</td>
    </div>

    <div style="display:none"><xsl:attribute name="id">history</xsl:attribute>
      <xsl:for-each select="//JobsReport/history/link">
	<xsl:sort select="@date" order="descending" />
	<h4>
	  <a>
	    <xsl:attribute name="title">old board</xsl:attribute>
	    <xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute>
	    <xsl:value-of select="@date"/>
	  </a>
	</h4>
	<br/>
      </xsl:for-each>
    </div>
    
</body>

</html>
</xsl:template>
</xsl:stylesheet>
