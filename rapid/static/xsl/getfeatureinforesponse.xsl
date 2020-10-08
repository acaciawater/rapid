<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:template match="/ServiceExceptionReport">
		<html>
			<body>
				<p>Service Exception!</p>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="/GetFeatureInfoResponse">
		<html>
			<body>
				<xsl:apply-templates select="Layer"></xsl:apply-templates>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="Layer">
		<h3>
			<xsl:value-of select="@name"></xsl:value-of>
		</h3>
		<table>
			<tr>
				<th>Feature</th>
				<th>Attribute</th>
				<th>Value</th>
			</tr>
			<xsl:apply-templates></xsl:apply-templates>
		</table>
	</xsl:template>
	<xsl:template match="Feature/Attribute">
		<tr>
			<td>
				<xsl:value-of select="../@id"></xsl:value-of>
			</td>
			<td>
				<xsl:value-of select="@name"></xsl:value-of>
			</td>
			<td>
				<xsl:value-of select="@value"></xsl:value-of>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="Attribute">
		<tr>
			<td>
				
			</td>
			<td>
				<xsl:value-of select="@name"></xsl:value-of>
			</td>
			<td>
				<xsl:value-of select="@value"></xsl:value-of>
			</td>
		</tr>
	</xsl:template>

</xsl:stylesheet>