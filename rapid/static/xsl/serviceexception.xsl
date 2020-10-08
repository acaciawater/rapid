<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:ogc="http://www.opengis.net/ogc">
<xsl:output method="html"/>
<xsl:template match="ogc:ServiceExceptionReport">
	<xsl:apply-templates select="ogc:ServiceException"/>
</xsl:template>
<xsl:template match="ogc:ServiceException">
	 <xsl:value-of select="@code"/>: <xsl:value-of select="."/>
</xsl:template>
</xsl:stylesheet>
